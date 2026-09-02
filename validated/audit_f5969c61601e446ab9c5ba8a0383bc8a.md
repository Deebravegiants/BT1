Based on this analysis, I've confirmed the vulnerability.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`/`webhook_id`) used to route and attribute the webhook are read directly from unauthenticated HTTP headers. The registry trusts these header-derived values without any cryptographic binding to the shop that supposedly sent the webhook.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside of the signed payload: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC and then hands the header-derived `shop` straight to the handler as the tenant identity, with no cross-check that the signed body actually belongs to that shop: [3](#0-2) 

This breaks the intended identity binding: `hmac_valid(raw_body) == true` should imply `shop_header == shop_that_produced(raw_body)`, but the library only proves `hmac_valid(raw_body) == true`; it never proves anything about which shop the body came from. Since Shopify webhook endpoints are plain public HTTP(S) URLs, any unprivileged internet user who can obtain one validly-signed `(raw_body, hmac)` pair — trivially, by installing the app on their own store and receiving one of their own legitimate webhooks — can replay that exact body to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g. a victim's shop). `HmacValidator.validate` will still pass because it only recomputes the HMAC over `raw_body`, and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled `shop` value.

### Impact Explanation
This is a cross-tenant identity-binding break in the gem's own webhook-processing code, not something that depends on the host app misusing an undocumented API — the gem itself hands the unauthenticated header value directly to the handler as the trusted "shop" for the event. Depending on how the host app keys its logic off the `shop` field in `WebhookMetadata` (e.g. session/token lookup, de-authorization on `app/uninstalled`, data updates keyed by shop), an attacker-controlled replay can make the app act on/against a victim tenant's data using content the attacker fully controls, satisfying the "cross-tenant access" Critical criterion.

### Likelihood Explanation
Any merchant who installs the app on their own store can trivially capture a validly-signed webhook (body + HMAC) for a mandatory or common topic. Webhook endpoints are public URLs reachable by any internet user, requiring no access token, `api_secret_key`, or privileged account — only the ability to replay one HTTP POST with a modified header.

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) header values into the signable string used for HMAC verification, or otherwise cryptographically tie the header-derived identity to the signed body, so that `HmacValidator.validate` fails if any of these fields are altered independently of the body.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `app/uninstalled`, whose body is `{}`), capturing the raw POST: headers including `X-Shopify-Hmac-Sha256: <valid_hmac_for_empty_body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and body `{}`.
2. Attacker replays the exact same request to the app's webhook endpoint, only changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= "{}"`) — this still matches the captured signature because the shop header isn't part of the signed content: [4](#0-3) [5](#0-4) 
4. `handler.handle` is invoked with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)`, causing the host app to process an uninstall (or other) event as if it genuinely came from the victim shop.

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
