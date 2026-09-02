This confirms the finding: `ShopifyAPI::Webhooks::Registry.process` explicitly documents that it "will verify the request did indeed come from Shopify" via HMAC, and the returned `WebhookMetadata.shop` field is what host apps use as the tenant identifier (per `docs/usage/webhooks.md`), yet the `shop` value is taken from an HTTP header never covered by that HMAC.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` (the data verified by `HmacValidator`) is defined as only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` treats a valid body HMAC as proof that the *entire request*, including these header-derived fields, originated from Shopify for the claimed shop, but the HMAC never binds the headers to the body.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`. [1](#0-0) 
For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 
Meanwhile, `shop`, `topic`, and `webhook_id` — the fields used to dispatch and attribute the webhook — are pulled straight from caller-supplied headers with no cryptographic binding to the body: [3](#0-2) 
`Registry.process` validates only the HMAC of the body, then dispatches based on `request.topic` and forwards `request.shop` as the trusted tenant identity to the app's handler: [4](#0-3) 

The intended identity binding is: `hmac_valid(body) == true` implies `(shop, topic, webhook_id, body)` as a whole is authentic and shop-attributed. In reality the code only proves `hmac_valid(body) == true` implies `body` is unmodified — the `shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers are never covered by the signature and can be freely set by anyone submitting the POST to the app's public webhook endpoint.

Because webhook endpoints are public HTTP routes (per `docs/usage/webhooks.md`, apps expose a route that directly builds `Request.new(raw_body: request.raw_post, headers: request.headers.to_h)` and calls `Registry.process`), any unprivileged internet user who has captured one legitimate `(raw_body, hmac)` pair — e.g., from their own trial/dev shop, which anyone can freely create — can replay that exact body/HMAC pair to a victim app's webhook endpoint while substituting the `shop-domain` header for a different (victim) shop domain. `Registry.process` will treat this as a validly-signed webhook "from" the victim shop, because the HMAC check never inspects the header at all. [5](#0-4) 

### Impact Explanation
Downstream host applications are explicitly told by this library's own documentation that `data.shop` is "the shop domain of the webhook" and is safe to key business logic on (job attribution, tenant-scoped queue processing, etc.). An attacker forging the `shop-domain` header can cause an app to attribute another shop's webhook data/events to a victim shop it doesn't own (or vice versa) — a cross-tenant confusion/access issue, since the app has no other means (within this gem) of confirming which shop actually sent the event. This satisfies the Critical "cross-tenant access" impact category, since the vulnerability lets one shop's traffic be misattributed to another tenant purely through this gem's request-verification logic.

### Likelihood Explanation
High. No secrets, TLS interception, or privileged access are required — only a normal, freely obtainable Shopify shop (even a free development store) to legitimately receive one real webhook delivery and HMAC, then replay it against the target app's public webhook URL with a forged `shop-domain`/`topic` header. This requires no interaction with the target beyond POSTing to its already-public webhook endpoint, which the documentation instructs developers to expose without additional header validation because the gem's `Registry.process` is advertised as verifying "the request did indeed come from Shopify."

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed payload used for `to_signable_string`, or otherwise cryptographically bind them to the HMAC-verified body (e.g., require the app to separately confirm the shop domain against a known/expected list of installed shops before trusting `request.shop`). At minimum, document prominently that `shop`, `topic`, and `webhook_id` are NOT covered by the HMAC and must not be trusted for tenant attribution without independent verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and legitimately receives a real
# Shopify webhook for it, e.g. for topic "customers/data_request":
#   raw_body = '{"customer":{"id":123},"shop_id":1}'
#   valid_hmac = <Shopify-computed HMAC for raw_body using the real api_secret_key>
#
# The attacker then replays the exact same raw_body/hmac to the target app's
# public webhook endpoint, only changing the shop-domain header:
headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => valid_hmac,               # valid for raw_body, unrelated to shop header
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged - not covered by HMAC
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC check passes (Utils::HmacValidator.validate only checks raw_body),
#    handler.handle is invoked with WebhookMetadata.shop == "victim-shop.myshopify.com",
#    even though the request has nothing to do with that shop.
``` [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
