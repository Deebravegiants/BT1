## Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC computed only over the raw request body. The `shop` (tenant identifier), along with `topic`, `webhook_id`, and `api_version`, are read directly from unauthenticated HTTP headers and are never part of the signed material. Because the same `api_secret_key` is shared across every shop that installs the app, any merchant can generate a body/HMAC pair that is valid for the shared secret and then replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, causing the receiving application to process attacker-controlled webhook data as if it came from a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all sourced from HTTP headers rather than from the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC purely against `verifiable_query.to_signable_string` (i.e., only the body): [3](#0-2) 

`Registry.process` performs this body-only HMAC check, and then constructs `WebhookMetadata` using the unauthenticated `request.shop` value that is handed directly to the application's webhook handler for tenant scoping: [4](#0-3) 

The identity binding the caller relies on is effectively:
`HMAC-verified(body) == HMAC-verified(body, shop)`

but this equality does not hold — `shop` is never included in the signed content. Since a single app's `api_secret_key` is shared by every shop that installs it, any unprivileged internet user who can install/uninstall the target app on their own store (a normal, unprivileged action available to anyone with a Shopify Partner/dev account) can trigger a legitimate webhook delivery for their own shop with attacker-chosen body content and a correctly-computed HMAC, then replay that exact `(body, hmac)` pair to the same shared webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. The HMAC check still passes because it only covers the body, and the host application's handler will process/store the forged payload as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant identity boundary the HMAC is meant to enforce and enables cross-tenant data injection/confusion in any multi-tenant application built on this gem's webhook-processing helper — data or actions the app associates with `shop` (e.g., writing "installed"/"uninstalled" state, order/product data, or triggering shop-scoped side effects) can be attributed to an arbitrary victim shop chosen by the attacker. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high in any typical Shopify app: the attacker only needs to be able to install the target app on a store they control (a normal, unprivileged capability), capture one legitimate webhook delivery containing attacker-controlled body content, and replay it with a modified shop header — no access to the app's `client_secret`/tokens, no privileged account, and no host application misconfiguration is required beyond following this gem's documented `Registry.process` usage.

### Recommendation
Bind the trusted `shop` (and ideally `topic`/`webhook_id`) to the cryptographic verification step rather than trusting header-derived values independently. Concretely: include the `shop-domain` header (and other security-relevant identity headers) in the HMAC-signable material, or require callers to independently verify that `request.shop` corresponds to a shop with an active, previously-established session/registration before acting on the payload. At minimum, `Registry.process`/`HmacValidator` should not present `request.shop` to handlers as "authenticated" data since only the body is actually covered by the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Attacker triggers a webhook (e.g., `products/create`) with a body of their choosing, and Shopify delivers it to the app's shared webhook endpoint with a valid `X-Shopify-Hmac-Sha256` computed with the app's shared `api_secret_key` over that raw body, plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this `(raw_body, hmac)` pair.
4. Attacker (or a script) replays a request to the same webhook endpoint with the identical `raw_body`/`hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC — it never checks the shop header — so `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and any application logic keyed off `shop` treats the attacker payload as belonging to `victim-shop.myshopify.com`.

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
