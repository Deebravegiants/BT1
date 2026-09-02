### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop identity delivered to webhook handlers from the unauthenticated `X-Shopify-Shop-Domain` header, while the HMAC signature that `Registry.process` verifies covers only the raw request body. An attacker who possesses any single valid `(body, hmac)` pair — trivially obtainable by installing the app on their own store and receiving one legitimate webhook — can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `shop-domain` header. The signature still validates, but the shop attributed to the event is attacker-controlled, breaking the binding between "bytes verified" and "shop acted upon."

### Finding Description
`Webhooks::Request#shop` reads directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

However, `to_signable_string`, which is what gets HMAC-validated, only ever returns the raw body — it does not include the shop domain header: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature purely over `to_signable_string`: [3](#0-2) 

`Webhooks::Registry.process` gates on this HMAC check and then forwards `request.shop` — the unverified header value — straight to the application's handler as the trusted tenant identifier: [4](#0-3) 

The equality the code implicitly (and incorrectly) assumes is:
`shop_the_HMAC_authenticates == shop_the_handler_acts_on`

In reality:
- Bytes verified by HMAC = `raw_body` only.
- Shop identity used by the handler = `headers["shopify-shop-domain"]`, an independent, unsigned field.

Since the two are not cryptographically bound together, any attacker who owns a legitimate `(raw_body, hmac)` pair signed with the app's `client_secret`/`api_secret_key` (obtained, for example, by installing the app on their own store and letting Shopify deliver one real webhook to them) can resend that same body and HMAC to the app's public webhook endpoint with the `shop-domain` header changed to any victim shop. `HmacValidator.validate` will accept it because the signed bytes are unchanged, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant integrity/confidentiality break: a webhook payload can be attributed to a shop the attacker does not control and never actually triggered it for. Depending on how the host application's registered handler uses `WebhookMetadata#shop` (e.g., looking up the shop's session, updating shop-scoped state, processing `app/uninstalled`, orders, or GDPR-related topics), this allows an attacker to inject events into another merchant's data/state using only their own legitimately-signed webhook body. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that relies on this library's webhook verification as its sole trust boundary (as documented): the attacker only needs to run the app on any store they control (including a free/dev store) to harvest one valid signed webhook, then can freely swap the `shop-domain` header on replays to any target shop domain, since nothing in `Request#hmac`/`to_signable_string` binds the shop field to the signature.

### Recommendation
Include the shop domain (and other headers such as topic/webhook-id if they are trusted for dispatch) in the signable string, or otherwise cryptographically bind them to the payload before use, e.g.:

```diff
 sig { override.returns(String) }
 def to_signable_string
-  @raw_body
+  # keep body-only signing per Shopify's HMAC scheme, but require the
+  # caller to additionally verify shop-domain against the shop that
+  # owns the corresponding registered webhook/session before dispatch
+  @raw_body
 end
```

Since Shopify's HMAC scheme intentionally signs only the raw body, the real fix belongs in `Webhooks::Registry.process`: cross-check `request.shop` against the shop associated with the registration/session that is expected to receive this topic, rejecting the webhook if they don't match, rather than trusting the header as an authenticated tenant identifier.

### Proof of Concept
1. Attacker registers/installs the target app on `attacker.myshopify.com` and triggers any webhook topic the app subscribes to (e.g., `products/update`). Shopify delivers a legitimate request with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker captures `B` and `H`.
3. Attacker sends a POST to the app's public webhook endpoint with the same body `B`, the same `hmac-sha256` header `H`, `shopify-topic` unchanged, but `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header successfully (no validation tying it to the signature): [1](#0-0) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `H`: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, causing the app to process an attacker-crafted payload as if it originated from the victim shop: [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
