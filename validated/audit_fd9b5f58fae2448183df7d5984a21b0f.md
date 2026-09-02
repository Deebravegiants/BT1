### Title
Webhook `shop` domain identity is passed to handlers without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then dispatches the request to the host application's handler using a `shop` value taken from an HTTP header that is **not** part of the signed material. This breaks the identity binding: `HMAC-verified(body) == tenant-attributed(shop-domain-header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which only checks `request.to_signable_string` (i.e., the body) against the computed signature — and then immediately constructs `WebhookMetadata` using the unverified `request.shop`, handing it to the app's handler as the tenant identity for that event: [4](#0-3) [5](#0-4) 

Because the HMAC only binds `secret ↔ raw_body`, and not `secret ↔ (raw_body, shop)`, any request that carries a previously-observed, validly-signed body (e.g. from a genuine webhook the attacker received for their *own* installed/trial shop) remains **HMAC-valid** even if the `shop-domain` header is swapped to name a different, victim shop. The gem provides no mechanism, and does not document a requirement, for the host application to cross-check `request.shop` against anything else before trusting it — `WebhookMetadata.shop` is handed to the handler as ground truth.

### Impact Explanation
This is a cross-tenant identity-confusion primitive: an unprivileged internet user who can install/operate their own trial shop (i.e., become a legitimate recipient of real, validly-signed webhook payloads) can replay a captured signed body while substituting the `shop-domain` header to point at another merchant. Any host application that uses `WebhookMetadata#shop` (as returned by this gem) to select which tenant's stored session/data to update, without an independent verification of that binding, will process the replayed event under the wrong tenant — leading to cross-tenant data corruption or state changes attributed to a shop the attacker does not own. Per the rubric this falls under **Critical - cross-tenant access**, since the vulnerable binding (`shop` identity vs. HMAC-authenticated payload) is defined and exposed entirely inside this gem's webhook processing code, not merely an application misuse of a documented contract.

### Likelihood Explanation
Exploitation only requires the attacker to (a) install the target app on their own shop to receive at least one genuine signed webhook, and (b) resend that exact body with a modified `shop-domain` header to the app's webhook endpoint (trivial to do since neither TLS pinning nor header-binding is required — the HMAC computation never looks at headers at all). No `api_secret_key`, access token, or privileged access is needed. The primary constraint is that the replayed payload's *content* must still make sense to the receiving handler for the target shop (e.g., generic/topic-level bodies, or bodies containing attacker-controlled data from their own shop that the handler blindly persists under `data.shop`), which is realistic for several common webhook topics.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable string, or independently verify `request.shop` against a value derived from something signed (e.g., look up the destination by a separately-authenticated identifier) before trusting it in `Registry.process`. At minimum, document prominently that `WebhookMetadata#shop` is **not** integrity-protected by the HMAC check and must not be used as the sole tenant selector by consuming applications.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives a genuine webhook, e.g. an "app/uninstalled" or generic topic event
# with body: raw_body = '{"id":1}'
# and header: x-shopify-hmac-sha256 = Base64(HMAC-SHA256(secret, raw_body))

# The attacker resends the exact same body + hmac header, but swaps only the
# shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic"        => "app/uninstalled",
  "x-shopify-hmac-sha256"  => captured_valid_hmac,      # unchanged, still valid for raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged, NOT covered by HMAC
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
# The host app's handler now believes this event legitimately originated
# from "victim-shop.myshopify.com".
``` [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

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
