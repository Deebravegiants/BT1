### Title
Webhook shop identity (`shop-domain` header) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, then hands the caller a `shop` value that is read straight from an unauthenticated HTTP header. Because the app's webhook signing secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every merchant that installs the app, any tenant who receives a genuine webhook can replay its body+HMAC to the same endpoint while substituting a different `shopify-shop-domain` header, and the library will accept it as a valid, authenticated webhook "from" the victim shop.

### Finding Description
The identity binding that should hold is:
`shop_attributed_to_webhook == shop_that_the_HMAC_actually_authenticates`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled directly from HTTP headers, never mixed into the signed content: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (the body) and compares it to the `hmac` header, with no reference to the shop header at all: [4](#0-3) 

`Registry.process` treats a passing HMAC check as full authentication of the request and forwards the unauthenticated `request.shop` value straight to the app's handler: [5](#0-4) 

Because Shopify apps use a single `api_secret_key`/`client_secret` for signing webhooks to **every** installed shop (this is not a per-tenant secret), the equality that `process` implicitly assumes — "if the HMAC verifies, then `request.shop` correctly identifies the tenant this body belongs to" — does not hold. The HMAC only proves "this body was HMAC'd with this app's shared secret" (i.e., it originated from *some* legitimate webhook delivery to *some* shop that has this app installed), not "this body belongs to the shop named in this header."

### Impact Explanation
Any shop that installs the app (an "unprivileged" tenant relative to other merchants) receives real webhooks with valid HMACs computed using the app's shared secret. That tenant can capture one such `(raw_body, hmac_header)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop's domain. `Registry.process` will validate the HMAC successfully (it never checked the shop header) and dispatch `WebhookMetadata` with `shop` set to the victim's domain and `body` containing the attacker-controlled payload from their own shop's webhook. If the host application uses `data.shop` to route/attribute the webhook body to a specific tenant's records (the intended and documented use of this field, see `docs/usage/webhooks.md`), this results in cross-tenant data injection/confusion — writing or acting on data under another merchant's identity. This satisfies the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker have their own working, ordinary installation of the target app (any free/trial account) to observe one genuine webhook delivery, which is trivial to obtain and requires no leaked credentials, no TLS interception, and no privileged access. The only "skill" needed is capturing and replaying an HTTP request with a modified header, which is within reach of any unprivileged internet user who can install the target Shopify app.

### Recommendation
Bind the shop identity into the authenticated content, or otherwise cryptographically tie the `shop-domain` header to the HMAC:
- Include the `shop` (and ideally `topic`/`webhook_id`) header value in the signable string used by `HmacValidator`, or
- Verify the `shop` header against the shop that Shopify's webhook payload body itself references (most Shopify webhook payloads include a shop-identifying field), and reject the request if there is a mismatch, or
- Document loudly (and consider enforcing) that consuming applications must cross-check `WebhookMetadata#shop` against a shop they already have a stored session/token for, and must not treat the header as trusted proof of tenant identity by itself.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, which is a legitimate installation and thus gets sent real webhooks (e.g., `orders/create`) HMAC-signed with the app's shared `client_secret`.
2. Attacker captures one such delivery:
   - `raw_body = '{"id":1,...attacker order json...}'`
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body under shared secret>`
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
3. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` and the shared secret and it matches (the shop header was never part of the computation), so `Registry.process` proceeds.
5. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's order data>, ...)` — the host application now processes attacker-controlled data as if it belongs to `victim.myshopify.com`.

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
