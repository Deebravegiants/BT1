### Title
Webhook `shop` field is not covered by the HMAC signature, allowing shop-attribution forgery on replayed webhook payloads - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by checking the HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `to_signable_string` used for that check returns only `@raw_body`, while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers that are never included in the signed material [2](#0-1) . After the HMAC check passes, `process` hands the unauthenticated `shop` header straight to the app's handler as trusted tenant identity [1](#0-0) .

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, bytes_bound_to_shop)`. Instead the gem verifies `hmac == HMAC(secret, raw_body)` while `shop` (and `topic`/`webhook_id`) are taken from separate, unsigned headers [3](#0-2) . `VerifiableQuery#to_signable_string` is the single point that determines what the HMAC is protecting [4](#0-3) , and for webhooks it is just the body:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [5](#0-4) 

Because of this, any entity capable of producing one valid `(raw_body, hmac)` pair for the configured `api_secret_key`/`old_api_secret_key` — for example a merchant who has legitimately installed the app and received one authentic webhook for their own shop — can replay that exact `(body, hmac)` pair while substituting an arbitrary `x-shopify-shop-domain` (and `topic`/`webhook-id`) header value. `Utils::HmacValidator.validate` will still return `true` since it only recomputes the HMAC over `@raw_body` [6](#0-5) , and `Registry.process` will then invoke the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where both `topic` and `shop` are the attacker-supplied, unverified header values [1](#0-0) .

### Impact Explanation
This breaks the tenant-identity binding the gem is supposed to establish for the app: an integrity-verified webhook payload is presented to the application as if it belonged to a shop domain that was never cryptographically confirmed. If the host app trusts `data.shop` from `WebhookMetadata` (as the gem's own webhook usage guidance encourages) to look up per-shop records, apply per-shop side effects, or route data, an attacker who is themselves an installed/authorized user of the app for shop A can cause the app to process a webhook body as though it originated from victim shop B — a cross-tenant data-attribution issue reachable purely by an app-installing party (no `api_secret_key`, no access token theft, no TLS interception needed).

### Likelihood Explanation
Requires the attacker to have obtained at least one genuine `(body, hmac)` pair, which is achievable simply by being a legitimate, unprivileged installer of the app on a shop they control and capturing one of the app's real webhook deliveries (webhook endpoints are public URLs by design, and the HMAC secret is shared across all shops for the app rather than per-shop). No credential compromise or elevated access is required beyond ordinary app installation, which is the intended unprivileged-user flow for this class of app.

### Recommendation
Include shop-identifying and topic fields in the HMAC-protected signable string (or otherwise cryptographically bind the header values to the payload before use), or clearly document/enforce that consumers must independently verify `WebhookMetadata#shop` against session/shop records they already trust before acting on it, rather than treating a passing HMAC check as authenticating the `shop` header.

### Proof of Concept
1. App installs `ShopifyAPI` and registers a webhook handler that trusts `data.shop` from `WebhookMetadata` (per the documented usage pattern).
2. Attacker installs the same app on their own shop `attacker-shop.myshopify.com` and captures a real webhook delivery, e.g. body `{"id":1}` with a valid `x-shopify-hmac-sha256` computed by Shopify over that body using the app's shared secret.
3. Attacker resends the same body and HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and any desired `x-shopify-topic`).
4. `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only and returns `true` [7](#0-6) ; `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` [1](#0-0) , causing the app to act as if the payload came from the victim shop.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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
