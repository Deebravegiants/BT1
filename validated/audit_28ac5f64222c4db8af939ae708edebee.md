### Title
Webhook shop identity is unauthenticated — HMAC only signs the raw body, letting a replayed request spoof `WebhookMetadata#shop` to any tenant - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once its HMAC validates, then hands the host application a `shop` value taken straight from the unauthenticated `X-Shopify-Shop-Domain` header. The HMAC signature never covers that header, so the equality the gem implicitly relies on — "HMAC-authenticated request" == "shop identity used to route/attribute the webhook" — does not actually hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled unauthenticated from HTTP headers: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. from the body bytes only: [3](#0-2) 

`Registry.process` then validates the HMAC and, on success, unconditionally forwards `request.shop` (the unauthenticated header) to the app's handler as the tenant identity, with no cross-check that this shop actually corresponds to the body or to any installed session: [4](#0-3) 

Because the header is not part of the signed material, any HTTP client that has captured one valid `(raw_body, HMAC)` pair — for example a legitimate webhook delivered to their own shop's app instance — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop that also has the app installed. `Utils::HmacValidator.validate` will still return `true` (the body and signature are unmodified and correctly signed), and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` is the attacker-chosen victim domain, causing the application to store or act on the replayed payload under the wrong tenant's identity.

### Impact Explanation
This breaks the tenant boundary the gem is expected to preserve: the "shop the HMAC proves the request came from" is not the same as "the shop stored/used downstream," which is exactly the class of identity-binding break called out (shop authenticated vs. shop used as the routing/session key). Since apps built on this gem are expected to use `WebhookMetadata#shop` from `Registry.process` as the authoritative tenant identifier (there is no alternative authenticated shop field provided by the gem), this results in cross-tenant webhook data being attributed to an arbitrary shop without needing the app's `client_secret`, an access token, or any privileged credential — only one previously observed legitimate webhook payload for any shop using the same app.

### Likelihood Explanation
An unprivileged user who has installed the same app on any shop (including a shop they own) can capture one legitimate webhook delivery and its `X-Shopify-Hmac-Sha256` value, then freely replay that exact body/HMAC to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a different, victim tenant. No secret material, admin access, or complex conditions are required beyond network access to the app's public endpoint, making this straightforward to reproduce.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise cryptographically tie the header-derived `shop` to the verified body before it is handed to `WebhookHandler#handle` — for example, requiring `Registry.process` to cross-check `request.shop` against an expected/registered shop for the given webhook subscription, or refusing to trust `request.shop` unless it can be independently correlated to a known active session, rather than passing the raw header value straight through as the trusted tenant identity.

### Proof of Concept
1. App exposes a webhook endpoint that calls `ShopifyAPI::Webhooks::Registry.process(request)`, where `request` is built via `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)`.
2. Attacker's own shop (App is installed there legitimately) receives a real webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC over `B` with the app's secret), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same `(B, H)` to the app's webhook endpoint but replaces the header with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) still succeeds because it only compares `H` against `HMAC(B, secret)`, and headers are irrelevant.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))`, causing the application to process/store attacker-controlled webhook content attributed to `victim-shop`.

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
