Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `shop` is read directly from the unauthenticated `shopify-shop-domain` header with no cryptographic binding to the HMAC [2](#0-1) . `Registry.process` validates only the HMAC and then trusts `request.shop` to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` value used to identify which merchant a webhook belongs to is read from a plain HTTP header that is never included in the signed payload. Anyone who can obtain one valid `(body, hmac)` pair — for example a merchant who has installed the app on their own store and can trigger a webhook to themselves — can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header, and the library's own verification will still say the request is valid.

### Finding Description
`ShopifyAPI::Webhooks::Request` includes `Utils::VerifiableQuery` and defines:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [4](#0-3) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the `hmac` field with a constant-time comparison [5](#0-4) . Because `to_signable_string` is only `@raw_body`, the signature verifies nothing about `shop`, `topic`, `api_version`, or `webhook_id` — those are taken verbatim, and unauthenticated, from HTTP headers via `shopify_header` [6](#0-5) .

`Registry.process` then does:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

The identity binding that should hold is: `shop asserted in the header == shop cryptographically bound to the signed content`. In this implementation, the equality never gets checked — the HMAC only proves "this body was signed with our app's secret at some point," not "this body belongs to shop X." Since the app's webhook signing secret (`api_secret_key`, i.e. the app's client secret) is shared across every shop that installs the app, any one merchant who installs the app can capture a legitimately-signed `(raw_body, hmac)` pair delivered to their own store (e.g., by triggering an `orders/create` webhook on their own shop) and then POST that identical body + HMAC directly to the app's public webhook endpoint with the `shop-domain` header changed to a different, victim shop's domain. `HmacValidator.validate` will report the request as valid because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is for the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook signature is meant to enforce: an app cannot actually trust that `WebhookMetadata#shop` reflects who the payload was really delivered to. A host application that keys any writes (e.g., disabling subscriptions, deleting data, updating shop-scoped billing state, GDPR redaction handling for `shop/redact`/`customers/redact`) off `request.shop`/`WebhookMetadata#shop` as returned by this library can be tricked into applying another shop's event to a victim shop it does not own, causing cross-tenant state corruption. This qualifies as Critical (cross-tenant access) under the given impact categories, since it requires no access token, no `api_secret_key`, and no privileged account — only a normal app installation available to any unprivileged merchant.

### Likelihood Explanation
Any merchant who installs the app is able to trigger events on their own store (e.g. creating an order or updating a product) and capture the resulting webhook body+HMAC sent to their app endpoint, since they control their own shop and can observe outbound webhook deliveries via a proxy or their own receiving code. Replaying that captured pair with a modified `shop-domain` header against the same public webhook endpoint requires no cryptographic secret and no special privileges — it's a straightforward HTTP replay against library code that never binds `shop` to the signed content.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the signable content used for HMAC verification, or otherwise cryptographically bind the shop domain to the signature rather than trusting it as a header. At minimum, `Webhooks::Request#to_signable_string` should incorporate `shop` so `HmacValidator.validate` fails whenever the shop header doesn't match what Shopify actually signed for that specific delivery, and `Registry.process` should reject a request if the shop bound to the signature disagrees with the header used for handler dispatch.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook for `orders/create`.
2. Attacker places an order on their own store, causing Shopify to deliver a legitimately-signed webhook to the app's endpoint:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: {"id": 123, ...}
   ```
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker sends a new POST directly to the app's public webhook endpoint with the identical body and HMAC header, but changes:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` [7](#0-6)  — it passes even though `shop` was changed.
6. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)`, causing the app to process attacker-controlled order data as though it belongs to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
