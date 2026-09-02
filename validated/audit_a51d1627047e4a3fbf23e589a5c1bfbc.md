## Title
Webhook shop/topic identity is read from unauthenticated headers while the HMAC only covers the raw body, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying that the raw request body matches an HMAC signature. The `shop`, `topic`, `webhook_id`, and `api_version` values that are actually acted upon (used to select the handler and passed to the application as the webhook's identity) come from HTTP headers that are never included in the signed content. Because the app's `api_secret_key` (the HMAC secret) is shared across every shop that installs the app, any attacker who installs the app on their own store can capture genuinely-signed webhook bodies and replay them with a forged `shop-domain`/`topic` header to make the receiving app believe the event originated from a different merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives its authenticated content strictly from the raw body: [1](#0-0) 

```
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

The `to_signable_string` method, used as the payload that is HMAC-verified, returns only the raw body: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `to_signable_string` (i.e., the body bytes) and compares it against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` then trusts `request.topic` and `request.shop` — both taken from unauthenticated headers — to select the handler and to populate the identity fields handed to the app's webhook handler: [4](#0-3) 

The binding that should hold is:
`shop/topic used by the handler == shop/topic that was cryptographically bound to this specific body`

Instead, the code only proves:
`raw_body bytes == HMAC(raw_body, api_secret_key)`

Because `api_secret_key` is the app's single shared secret (identical for every merchant that installs the app), any unprivileged internet user can install the app on their own shop, capture a real, validly-signed webhook delivery, and then resend those exact bytes to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header with a victim shop's domain/topic. `HmacValidator.validate` will still succeed (the body bytes are unchanged and correctly signed with the shared secret), and `Registry.process` will hand the forged `shop`/`topic` straight to the application's handler as if the event genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to provide app developers: the `shop` value delivered to webhook handlers is not actually authenticated, only the body content is. An attacker can make the app process attacker-controlled webhook payloads under the identity of an arbitrary victim shop (cross-tenant), which can drive any app logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop state, creating records, revoking access, syncing data) using a victim's identity. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires being able to install the target app on an attacker-owned development/trial store (a standard, unprivileged action any internet user can take with a public Shopify app) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint. No access token, leaked credential, or privileged account is required — the shared `api_secret_key` is used exactly as designed by Shopify's own webhook delivery to the attacker's own shop; the attacker merely reuses the resulting valid signature with substituted headers.

### Recommendation
Bind the identity fields into the material that is HMAC-verified, or otherwise cryptographically tie the header values to the signed payload before they are trusted:
- Include `shop`, `topic`, and `webhook_id` (not just the raw body) in the signable string that `HmacValidator` verifies, or
- Require the receiving application to independently confirm that the `shop-domain` header matches a shop for which this app is actually installed (e.g., cross-check against stored session/shop records) before invoking the handler, and document this requirement prominently since the gem currently provides no such binding.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development shop `attacker.myshopify.com`; the app registers a webhook (e.g., `orders/create`).
2. Shopify delivers a genuine webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid signature over body>` and some JSON body the attacker fully controls (they created the order).
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
4. Attacker crafts a new HTTP request to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` succeeds because it only checks `raw_body` against the (still valid) signature: [5](#0-4) 
6. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's body content, even though that shop never sent this webhook: [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
