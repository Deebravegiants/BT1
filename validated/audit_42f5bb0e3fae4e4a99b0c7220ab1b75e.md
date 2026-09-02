### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw body only, while the `shop` (tenant identifier) is read from the unauthenticated `X-Shopify-Shop-Domain` header. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then blindly trusts `request.shop` when building `WebhookMetadata` for the handler, breaking the binding `HMAC-covered-bytes == acted-upon shop`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `Request#shop` is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` then calls `verifiable_query.to_signable_string`, i.e. it only ever checks the body bytes against the app's `client_secret`-derived HMAC, never the shop header: [3](#0-2) 

`Registry.process` performs exactly this check and, once it passes, forwards `request.shop` unchanged into `WebhookMetadata`, which the host application uses to key data by tenant (per the gem's own documented example, `shop_domain: data.shop`): [4](#0-3) 

The binding that should hold is: `bytes covered by HMAC == bytes the handler treats as authoritative for tenant identity`. Here it does not: HMAC covers `body`, but the identity used to route/attribute the webhook is `shop`, an independent, unauthenticated header value. Since every webhook for every shop of a given app is signed with the same `client_secret` (Shopify does not use a per-shop signing key), a genuine merchant who is a legitimate app installer receives real webhook deliveries with a valid HMAC for their own body/topic. That same person can replay the identical `raw_body` + `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header naming a different, victim tenant. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain.

This is exactly the "field acted on but not covered by the HMAC" class: the gem itself, not just the host app, performs and documents this exact validate‑then‑trust flow (the usage docs literally say `Registry.process` "will verify the request did indeed come from Shopify" before handing off `data.shop`), so the gem is asserting a security property (`shop` is authenticated) that its own code does not provide.

### Impact Explanation
An attacker who is any regular merchant with an app installed (unprivileged relative to other tenants of the same app) can cause the host application to process a forged webhook attributed to a shop domain of their choosing. Because `WebhookMetadata#shop` is the sole tenant identifier the gem exposes to handlers, and the documented usage pattern is to key downstream work by `data.shop`, this crosses the tenant boundary: an attacker on shop A can inject fabricated webhook events (with a body of their own choosing, as long as it round-trips through their own valid HMAC) that the app will believe originated from shop B. This is a cross-tenant access primitive that does not require the app's `client_secret`, an access token, or any credential beyond having a working installation of the target app on the attacker's own store.

### Likelihood Explanation
Likelihood is high for any app that relies on the gem's advertised webhook-processing flow: no special network position, credential theft, or admin access is required — only the ability to install the app on one's own shop (or replay a webhook one legitimately received) and to send a crafted HTTP request to the app's public webhook endpoint with a doctored `shop-domain` header.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) values into the signed material that `HmacValidator` checks, or otherwise cryptographically tie the shop-domain header to the HMAC (e.g., include it in `to_signable_string`, or require the caller to independently verify `request.shop` corresponds to a shop with an active, previously-established session/registration before trusting it). At minimum, document prominently that `request.shop` is unauthenticated and must be cross-checked by the host application against a known/registered shop before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a webhook to the app with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(client_secret, B)`, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC_SHA256(client_secret, B)` from `to_signable_string` (the body) and compares to `H` — this still matches, per: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: B, ...)`, per: [6](#0-5) 
6. The host application, following the gem's documented pattern of keying work off `data.shop`, processes attacker-controlled data as belonging to `victim-shop`.

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
