### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` header (and `topic`/`webhook-id` headers) taken from the same request to route the payload to the app's handler as the identified tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and the HMAC is computed/verified over that signable string via `Utils::HmacValidator.validate_signature` / `compute_signature` [2](#0-1) . However, `Request#shop`, `#topic`, and `#webhook_id` are all read directly from HTTP headers (`shopify-shop-domain`/`x-shopify-shop-domain`, etc.) which are never part of the HMAC-covered content [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity forwarded to the app's `WebhookHandler`, with no cryptographic binding between the verified body and the claimed shop: [4](#0-3) 

This is exactly the "field acted on but not covered by the HMAC" bug class from the reference report: the signature proves the *body* came from a holder of the app's `client_secret` (i.e., genuine Shopify), but it proves nothing about which shop the header claims to be from. Any header (`shop-domain`, `topic`, `webhook-id`) can be swapped on a request that carries a validly-signed body without invalidating the HMAC check.

### Impact Explanation
If an attacker can obtain any one validly-signed `(raw_body, hmac)` pair produced by Shopify for the app's `client_secret` (e.g., a delivery for their own shop, or any interceptable/replayable delivery), they can resubmit it to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop. Because `HmacValidator.validate` only checks the body against the secret and never binds it to the shop, the request passes verification, and the handler receives `WebhookMetadata` claiming the victim shop as the source of attacker-influenced body content — a cross-tenant data-integrity break (violates `verified body == body actually originating from claimed shop`). This maps to the "Critical – cross-tenant access" impact category since it lets one tenant's webhook data be attributed to and processed under a different tenant's identity.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuine, validly-signed `(body, hmac)` pair for the app (e.g. from their own shop's legitimate webhook traffic, which they can trigger themselves as an ordinary merchant/app installer) and the ability to POST directly to the app's public webhook endpoint with modified headers — both of which are within reach of an unprivileged internet user/app installer and do not require the `api_secret_key`, TLS interception, or any privileged account. Likelihood is therefore moderate: it needs a self-triggered legitimate webhook to reuse, but no secret material or MITM position.

### Recommendation
Bind the identifying fields into the signed payload rather than trusting bare headers:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, e.g. by having the app-side registration record the expected shop/topic pair and cross-checking it against a value obtained from a trusted source such as a freshly-fetched Admin API call), so that the HMAC verifies the full tuple `(shop, topic, webhook_id, body)`, not just `body`.
- At minimum, document/enforce that `WebhookHandler` implementations must not treat `WebhookMetadata#shop` as a trusted tenant key unless it is corroborated against an independently established session/tenant identity.

### Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker.myshopify.com" and
# triggers a real event (e.g. creates an order) to receive a legitimately
# Shopify-signed webhook delivery at the app's shared endpoint:
#   headers: { "shopify-shop-domain" => "attacker.myshopify.com",
#              "shopify-topic" => "orders/create",
#              "shopify-hmac-sha256" => "<valid-hmac-of-body>" }
#   body: '{"id":1,"note":"malicious-payload"}'

# Attacker resends the exact same body + hmac, but rewrites the shop header:
request = ShopifyAPI::Webhooks::Request.new(
  raw_body: '{"id":1,"note":"malicious-payload"}',
  headers: {
    "shopify-topic" => "orders/create",
    "shopify-hmac-sha256" => captured_valid_hmac, # unchanged, still matches raw_body
    "shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  },
)

# HmacValidator.validate(request) still returns true, because the signature
# only covers @raw_body, not the shop header.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app processes attacker-controlled content as if it belongs to victim-shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
