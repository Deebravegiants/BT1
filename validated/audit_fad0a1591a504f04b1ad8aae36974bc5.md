## Analysis

The Maple bug class here is "a value is computed/trusted without being bound to the thing whose integrity was actually checked." The closest reachable analog in this gem's own code (excluding generated REST resources) is the webhook processing path, where the HMAC only covers the request body, but the `shop` field used to route/scope the webhook payload is taken from an unauthenticated header. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` proves that the body bytes were signed with the app's shared secret — it says nothing about which shop the request is "from." `Registry.process` reads `request.shop` straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header and passes it, unverified, to the handler as the tenant identifier.

### Finding Description
The equality the code should guarantee is: `shop bound by HMAC == shop delivered to handler`. Instead:
- `hmac` = `HMAC(api_secret_key, raw_body)` [4](#0-3) 
- `to_signable_string` = `raw_body` only, excluding `shop`, `topic`, `webhook_id`, `api_version` [5](#0-4) 
- `Registry.process` validates only that HMAC, then forwards `request.shop` (header-derived) to the handler as the tenant key with no further check [3](#0-2) 

Since `api_secret_key` is a single app-level secret shared across every shop that installs the app (not a per-shop secret), any merchant who installs the app can obtain genuinely-HMAC-valid `(raw_body, hmac)` pairs from their own legitimate webhook deliveries. Because the `shop-domain` header is excluded from the signable string, that merchant can resend the same `raw_body`/`hmac` pair to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` (it only re-derives the HMAC over `raw_body`), so `Registry.process` dispatches the payload to the handler labeled as coming from the victim shop.

### Impact Explanation
This breaks the tenant boundary the whole `Webhooks::Registry` API is built to enforce: the `shop` value handed to `WebhookMetadata`/handler code is the only tenant discriminator provided by this gem, and host apps are expected to trust it once `HmacValidator.validate` succeeds. An attacker (any merchant who installed the app — an unprivileged party relative to other tenants) can make the app process attacker-controlled webhook bodies under a victim shop's identity, i.e., cross-tenant data injection/confusion, without needing the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
Requires only that the attacker (a real, self-service merchant) installs the app to receive one legitimately signed webhook, then replays it with a modified shop header to the same publicly reachable webhook endpoint. No secrets need to be stolen and no TLS interception is required — a single benign installation suffices.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the value that is cryptographically bound, or otherwise verify `request.shop` against an expected/allow-listed shop for the delivery before dispatch — e.g., compare against the shop the webhook was registered for, or require the host application to independently confirm shop identity for any state-changing effect. At minimum, document that `request.shop` is not authenticated by `HmacValidator.validate` and must not be trusted as a tenant key on its own.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers a webhook.
2. Shopify delivers a real webhook: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends `POST` to the app's webhook endpoint with the same body `B` and same `H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is still `B`; `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches `H`, returning `true`. [2](#0-1) 
5. `Registry.process` proceeds and calls the handler with `shop: "victim-shop.myshopify.com"`, `body: B` — attacker-controlled data is processed under the victim tenant's identity. [3](#0-2)

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
