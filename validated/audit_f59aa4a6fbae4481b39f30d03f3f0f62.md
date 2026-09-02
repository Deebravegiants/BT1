### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` (parsed from the `x-shopify-shop-domain` / `shopify-shop-domain` header) is a separate, unsigned field. `Registry.process` trusts `request.shop` as the tenant identity passed to the app's webhook handler, but this value is never bound to the HMAC that `HmacValidator` checks. Any party who can obtain one validly-signed webhook body/HMAC pair (e.g., by owning their own shop that has the app installed) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, since the signature never covers that header.

### Finding Description
The webhook signature validation flow is: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string`: [2](#0-1) 

And for `Webhooks::Request`, `to_signable_string` is defined as just the raw body — it does not include the `shop`, `topic`, or `webhook_id` headers: [3](#0-2) 

After `HmacValidator.validate(request)` succeeds, `Registry.process` extracts `request.shop` directly from the (unsigned) header and hands it to the handler as the tenant identity in `WebhookMetadata`: [4](#0-3) 

This is the same class of bug described in the external report: an action (`handler.handle` operating on behalf of shop X) is authorized using a field (`shop`) that is never checked against — or bound into — the cryptographic proof (HMAC over body) that supposedly authenticates the request. The equality that should hold is:

```
hmac == HMAC(secret, body || shop || topic)
```

but the gem only enforces:

```
hmac == HMAC(secret, body)
```

leaving `shop` (and `topic`) attacker-controllable independent of the signature.

### Impact Explanation
Because the app's `api_secret_key` is shared across all shops using the app (it is not per-shop), an unprivileged user who merely installs the app on their own shop can obtain a legitimately Shopify-signed `(body, hmac)` pair for a webhook topic they control the content of (e.g., by triggering `orders/create`, or receiving mandatory topics like `customers/data_request`/`shop/redact`/`app/uninstalled`). They can then replay that exact body and HMAC to the merchant app's webhook endpoint while forging the `x-shopify-shop-domain` header to name a victim shop. `HmacValidator.validate` will report the signature as valid (it only checks the body), and `Registry.process` will invoke the registered handler with `WebhookMetadata#shop` set to the forged victim shop. Any app logic that keys off `data.shop` to select tenant-specific storage, permissions, or destructive actions (e.g., mandatory `shop/redact`, `customers/redact`, `app/uninstalled` handling) can be triggered against a shop the attacker has no relationship with — a cross-tenant integrity/authentication break attributable to this gem's own verification code.

### Likelihood Explanation
Exploitation only requires the attacker to install the app on a shop they control (an ordinary, unprivileged action any Shopify merchant can take) and to receive one webhook delivery from Shopify for that shop — no `api_secret_key`, access token, or other privileged credential is needed. The forged replay is a straightforward HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the tenant/topic identity into the signature verification: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, e.g., by requiring the app to independently verify `shop` against an expected/registered shop before trusting `WebhookMetadata#shop`), so that `HmacValidator.validate` fails whenever any of the header-derived tenant fields have been altered relative to what Shopify actually signed.

### Proof of Concept
```ruby
# Attacker owns "attacker.myshopify.com" and has installed the app.
# Shopify delivers a legitimately signed webhook to the attacker's own endpoint:
raw_body = '{"id":1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
encoded_hmac = Base64.encode64(hmac)

# Attacker replays the same body/hmac to the merchant app's webhook endpoint,
# but forges the shop-domain header to claim it's from "victim.myshopify.com":
forged_headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => encoded_hmac,
  "x-shopify-shop-domain" => "victim.myshopify.com", # forged - not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (only raw_body is checked),
#    handler.handle receives data.shop == "victim.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
