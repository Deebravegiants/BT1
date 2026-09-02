### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are taken from unauthenticated HTTP headers and passed straight to the app's webhook handler, are never included in the signed payload. Any party that possesses one valid `(body, hmac)` pair — trivially obtainable by installing the app on their own store and receiving a real webhook — can replay that exact body/HMAC pair while freely rewriting the `shop-domain` (and other) headers to impersonate a different, victim merchant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from headers that are never mixed into the signed string: [2](#0-1) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header — again, only the body is covered: [3](#0-2) 

`Registry.process` performs exactly this one check, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the metadata handed to the app's handler: [4](#0-3) 

The binding the library is supposed to enforce is:
`hmac_valid(raw_body) == true` should imply `shop_header == shop_that_the_payload_actually_belongs_to`.

In reality the equality only holds for `raw_body`; `shop_header` (and `topic`, `webhook_id`, `api_version`) are decoupled from the signature entirely. An attacker who legitimately installs the app on their own store (an "unprivileged internet user" with no special credentials, access tokens, or `api_secret_key` knowledge) will receive real, validly-signed webhooks for their own shop. They can then POST the exact same `raw_body` and `hmac` header to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a different, victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim shop.

### Impact Explanation
Any host application that keys per-tenant logic (e.g., "which merchant does this order/webhook belong to", session/record lookups, billing, fulfillment triggers) off `WebhookMetadata#shop` as supplied by this gem is exposed to cross-tenant data injection/impersonation: an attacker-controlled webhook body can be attributed to any victim shop domain, without needing that shop's credentials. This matches the Critical "cross-tenant access" impact category, since the identity binding between the authenticated bytes (body) and the acted-upon tenant identifier (shop) is broken by the gem's own verification routine.

### Likelihood Explanation
Likelihood is high: the only prerequisite is that the attacker has (or can create) a shop with the app installed so that they receive at least one legitimately-HMAC-signed webhook delivery. No secret keys, tokens, or TLS interception are required — only header manipulation on a subsequent direct POST to the app's public webhook endpoint, which is exactly the scenario this analog rule targets ("a field acted on but not covered by the HMAC").

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used for HMAC validation, or otherwise cryptographically bind them to the raw body (e.g., have `Request#to_signable_string` concatenate these header values with the body before computing/verifying the digest), so that a replayed payload cannot be re-attributed to a different shop or topic without invalidating the signature.

### Proof of Concept
1. Install the target app on an attacker-owned store `attacker-shop.myshopify.com` and capture one legitimate webhook delivery, e.g.:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid_hmac_for_body>
x-shopify-shop-domain: attacker-shop.myshopify.com
x-shopify-webhook-id: abc-123

{"id":1,"note":"hello"}
```
2. Replay the identical body and `hmac-sha256` header, but change only the shop header to the victim's domain:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same_valid_hmac_for_same_body>
x-shopify-shop-domain: victim-shop.myshopify.com
x-shopify-webhook-id: abc-123

{"id":1,"note":"hello"}
```
3. `ShopifyAPI::Utils::HmacValidator.validate` (as shown in `lib/shopify_api/utils/hmac_validator.rb`) still returns `true` because it only hashes `raw_body`. `ShopifyAPI::Webhooks::Registry.process` (see `lib/shopify_api/webhooks/registry.rb`) dispatches the app's handler with `shop: "victim-shop.myshopify.com"`, even though the payload was never generated for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
