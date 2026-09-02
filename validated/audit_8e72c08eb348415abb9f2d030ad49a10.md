### Title
Cross-tenant webhook spoofing via shop identity not covered by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the shop-identifying header (`shop-domain`, plus `topic`/`webhook-id`/`api-version`) is never included in the HMAC-signed material. This breaks the identity binding `shop authenticated == shop that produced the signed bytes`, letting a merchant who legitimately receives real webhooks from Shopify (i.e., any app installer, an "unprivileged" party relative to *other* tenants of the same app) replay that valid `(body, hmac)` pair while forging the `shop-domain` header to impersonate a different, victim shop.

### Finding Description
`HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For OAuth callbacks, `AuthQuery#to_signable_string` includes `shop` in the signed parameters, so `shop` is cryptographically bound to the HMAC there: [2](#0-1) 

However, for webhooks, `Webhooks::Request#to_signable_string` returns **only** `@raw_body`: [3](#0-2) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are never part of the signed bytes: [4](#0-3) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body HMAC) and then forwards `request.shop` (the unauthenticated header) straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [5](#0-4) 

The documented usage pattern explicitly tells app developers to trust `data.shop` as "The shop domain of the webhook" and use it to route/attribute the payload (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [6](#0-5) 

**Attack path:** A user who controls a shop that has installed the app (and therefore legitimately receives real, correctly-HMAC'd webhooks for their own store from Shopify) can capture one such `(raw_body, x-shopify-hmac-sha256)` pair. They then replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain (and optionally forged `topic`/`webhook-id`). Because the HMAC only covers `raw_body`, which is unchanged, `HmacValidator.validate` still succeeds — the attacker never needs `api_secret_key`. `Registry.process` then dispatches to the handler with `WebhookMetadata#shop == victim_shop` but `body` == the attacker's own shop's data. Since the gem documents `data.shop` as the authenticated tenant identifier, any host application following this API (as instructed) will misattribute/act on the payload under the wrong tenant — a cross-tenant identity confusion introduced entirely within this gem's verification logic, not a host bug.

### Impact Explanation
This is a **cross-tenant** vulnerability: the identity binding `shop (trusted, HMAC-covered) == shop (acted upon)` is broken, satisfying the report's "Critical — cross-tenant access" category. An attacker with no access token, no leaked credentials, and no privileged account (only their own legitimate, self-controlled installation) can cause the library to hand a host application a webhook payload falsely attributed to another merchant's shop, enabling cross-tenant data confusion/injection in any application built per this gem's documented contract.

### Likelihood Explanation
Likelihood is high for exploitation feasibility (any app installer can capture a real signed webhook body/HMAC pair trivially, since Shopify sends these to every installed app) but the severity of the ultimate exploitation depends on what the host application does with `data.shop` — since the gem's own docs instruct developers to key work off `data.shop`, most integrations following the documented pattern are affected.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material verified by `HmacValidator`, e.g. incorporate `shopify_header("shop-domain")` into `to_signable_string` or perform an explicit secondary comparison. At minimum, `Webhooks::Request` should treat `shop` as authenticated only when it is bound into the same signed payload; instead, it currently exposes an unauthenticated header value under the same accessor name/contract as an authenticated field.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook (e.g. `orders/create`) to the app's callback endpoint. Attacker captures the exact `raw_body` and the `x-shopify-hmac-sha256` header value Shopify sent.
2. Attacker replays an HTTP POST to the same webhook endpoint with:
   - `x-shopify-hmac-sha256`: unchanged (still valid for the same `raw_body`)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com`
   - `x-shopify-topic`, `x-shopify-webhook-id`: optionally forged
   - body: unchanged `raw_body`
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request; `HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, per: [7](#0-6) [8](#0-7) 
4. `Registry.process` passes validation and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, per: [5](#0-4) 
5. Any host application following the documented pattern (`shop_domain: data.shop`) now processes attacker-controlled data under the victim shop's identity.

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
