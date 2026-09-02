### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signature over the raw body only, while the `shop` (and `topic`/`webhook_id`) values used by the application come from separate, unsigned HTTP headers. `Registry.process` accepts any request whose body HMAC validates and then unconditionally trusts `request.shop` — which is not part of the signed material — when dispatching to the handler.

### Finding Description
`Utils::VerifiableQuery#to_signable_string` for webhooks returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into the signable string: [2](#0-1) 

`HmacValidator.validate` only checks `hmac == HMAC(secret, to_signable_string)`, i.e. `HMAC(secret, raw_body)`: [3](#0-2) 

`Registry.process` gates on this same validation and then trusts `request.shop` for dispatch, without any secondary binding between body and shop: [4](#0-3) 

The identity equality that should hold is: `shop_bound_by_hmac == shop_used_by_handler`. Here the HMAC only binds `raw_body`, so this equality never actually holds — `shop` is a value the caller of `Request.new` supplies out-of-band from headers, entirely outside the signed payload.

Because a single app-level `client_secret` (the same webhook signing key) is shared across every shop that has installed the app, any shop that legitimately installs the app can obtain a genuinely Shopify-signed `(raw_body, hmac)` pair for its own store (e.g., by triggering an event and capturing the resulting webhook delivery). That attacker-controlled shop can then replay the exact same `raw_body`/`hmac-sha256` header to the app's webhook endpoint while substituting the `shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` forwards `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` to the handler with `shop` set to the victim's domain.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an app built on this gem, following its documented webhook-processing API (`Registry.process`), cannot distinguish a genuine webhook for shop A from an attacker-forged one claiming to be shop B, as long as the attacker has captured any one valid signed payload from their own store. Depending on how the host application keys data off `WebhookMetadata#shop` (e.g., looking up the victim's session/access token, writing/deleting victim data, or triggering GDPR redaction/data-request flows using the attacker-chosen shop identity), this results in cross-tenant data manipulation or disclosure — satisfying the "cross-tenant access" Critical-impact bucket. This is a defect in the gem's own webhook verification primitive (`HmacValidator`/`Webhooks::Request`), not a misuse of an undocumented API by the host app; `Registry.process` is the gem's documented processing entry point.

### Likelihood Explanation
Requires no possession of `api_secret_key`, no access token, and no privileged account beyond being any (unprivileged) merchant able to install the target app on their own store and capture one legitimate webhook delivery — a normal, low-friction action. The replay itself is a trivial HTTP request with a modified header. Likelihood is High.

### Recommendation
Bind the shop (and topic/webhook id) identity into the verified signature material, or otherwise cryptographically tie the header-derived `shop` to the signed body — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or require the host application to independently verify that `shop` corresponds to a shop with a valid, previously stored session/installation before trusting `WebhookMetadata#shop`. At minimum, document prominently that `Webhooks::Request#shop` is unauthenticated and must not be trusted as a tenant identifier by itself.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (a normal, unprivileged action) and triggers a webhook-eligible event (e.g., updates a product). Shopify delivers a webhook to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac>`, and some `raw_body`.
2. Attacker intercepts this request (e.g., via a proxy they control, or by using a webhook debugging endpoint they configure) and notes `raw_body` and `X-Shopify-Hmac-Sha256`.
3. Attacker crafts a new HTTP request to the same app webhook endpoint using the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`. `HmacValidator.validate(request)` succeeds because it only hashes `raw_body`, which is unchanged. [5](#0-4) 
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and processes the attacker's payload as if it originated from the victim shop, despite the victim never sending anything.

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
