Confirmed root cause. Here's the analysis.

### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant/handler routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the raw request body against the HMAC signature, then dispatches to a handler and constructs `WebhookMetadata` using the `shop`, `topic`, `api_version`, and `webhook_id` values taken directly from unauthenticated HTTP headers. None of these header values are part of the signed material, so the binding "HMAC-verified bytes == data acted upon" is broken for every field except the raw body.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` then trusts `request.topic` (unauthenticated header) to select which registered handler to invoke, and `request.shop` (also an unauthenticated header) to populate the `WebhookMetadata` passed to that handler: [3](#0-2) 

`request.topic` and `request.shop` are read straight from the `shopify-topic`/`x-shopify-topic` and `shopify-shop-domain`/`x-shopify-shop-domain` headers with no relation to the signed payload: [4](#0-3) 

The identity/authorization binding that should hold is:
`HMAC-verified(raw_body) == (topic, shop) used for handler dispatch and tenant attribution`

This equality does not hold: the HMAC only proves the **body bytes** were signed with the app's shared `client_secret`; it says nothing about which shop or topic that body belongs to. Because the app's `client_secret` (and thus the HMAC key) is the same across every shop that installs the app, any merchant who installs the app receives legitimate webhooks (valid body + valid HMAC) for their own shop. That merchant — an otherwise unprivileged party with respect to any other tenant of the same app — can take a captured, validly-signed `(raw_body, hmac)` pair from their own shop's webhook and resubmit it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header (any other merchant's domain) and/or an arbitrary `shopify-topic` header (e.g. changing `orders/create` to `app/uninstalled` or `customers/data_request`). `HmacValidator.validate` still succeeds because it only checks the body against the shared secret, and `Registry.process` will happily route the request to whichever handler is registered for the attacker-chosen topic, constructing a `WebhookMetadata` that falsely attributes the (attacker-controlled) body/topic to a victim shop the attacker does not control.

### Impact Explanation
This crosses a tenant boundary using only credentials the attacker legitimately possesses (their own shop's webhook secret access), letting them:
- Feed forged/cross-tenant data into any handler registered by the host app, tagged with an arbitrary victim `shop` value (`WebhookMetadata#shop`), so the host application's business logic acts on data as if it originated from a different merchant — cross-tenant confusion.
- Trigger sensitive mandatory-webhook handlers (`shop/redact`, `customers/redact`, `customers/data_request`) for a victim shop identifier of the attacker's choosing by relabeling the `topic` header on a body they control, since `Registry.process` never checks that the signed body actually corresponds to the claimed topic or shop.

This matches the "cross-tenant access" Critical impact category, since the host application (following the gem's documented API) has no way to distinguish a genuinely-routed webhook from a relabeled one — the gem's own validation logic provides no such guarantee.

### Likelihood Explanation
Any developer/merchant who has installed the target app can trivially capture one legitimate webhook delivery for their own shop (valid body + valid HMAC, since the secret is shared per-app, not per-shop) and replay it with modified `shop`/`topic` headers via a simple HTTP request — no secret key, access token, or privileged access to the victim's shop is required.

### Proof of Concept
```ruby
# Attacker's own shop legitimately triggers a webhook delivery for topic "orders/create":
raw_body = '{"id":1,...}'           # attacker's own order data
hmac     = <valid HMAC-SHA256 of raw_body signed with the app's shared client_secret>
# (attacker receives this pair as their own legitimate webhook delivery)

# Attacker resends the SAME (raw_body, hmac) pair to the app's webhook endpoint,
# but swaps the headers to impersonate a victim shop and a sensitive topic:
headers = {
  "x-shopify-topic"       => "customers/data_request", # attacker-chosen, unsigned
  "x-shopify-hmac-sha256" => hmac,                      # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler for "customers/data_request" is invoked with
#    WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "customers/data_request", body: attacker's body, ...)
```
`Registry.process` performs no check that `raw_body`/`hmac` was actually issued for the claimed `topic` or `shop`: [3](#0-2) 

### Recommendation
Bind `shop`, `topic`, `api_version`, and `webhook_id` into the signed material (or otherwise cryptographically tie the header values to the signature) so `HmacValidator.validate` fails whenever any of these fields is tampered with. At minimum, document and/or enforce that host applications must independently verify the `shop` domain against their own session store before trusting `WebhookMetadata#shop`, since the gem itself currently offers no such guarantee for header-derived fields.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
