### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw HTTP body only, while the `shop` (tenant identifier) is read from an unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then forwards this unauthenticated `shop` value straight into the `WebhookMetadata` handed to the app's webhook handler, which per this gem's own documentation is expected to use `data.shop` as the tenant key. This breaks the identity binding `shop_that_produced_the_valid_HMAC == shop_used_for_tenant_routing`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed payload: [2](#0-1) 

`HmacValidator.validate` (used by `Registry.process`) only checks `verifiable_query.hmac` against a signature computed over `verifiable_query.to_signable_string`, i.e., the raw body — the `shop` header plays no part in the check: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` from `request.shop`, the unauthenticated header value, and passes it to the app-supplied handler: [4](#0-3) 

The gem's own documentation instructs app authors to trust `data.shop` as "The shop domain of the webhook" and to use it directly as the tenant key for downstream processing (e.g. `shop_domain: data.shop`): [5](#0-4) 

Because the app's `client_secret`/`api_secret_key` is shared across **every merchant** that has installed the app, any merchant is able to obtain a body+HMAC pair that validates successfully (from their own legitimate webhook deliveries). Since the `shop` header is not part of the signed content, that same valid `(raw_body, hmac)` pair remains valid no matter what `shop` header value accompanies it. This is the exact analog of the reported bug class: a field that is acted upon (`shop`, used for tenant routing) is not covered by the authentication mechanism (`hmac`) that is supposed to bind it to the request.

### Impact Explanation
This allows any existing merchant of the app (an "unprivileged" party with respect to other tenants) to forge a webhook request that passes signature verification while claiming to originate from an arbitrary victim shop domain. Since apps are documented to trust `data.shop` for tenant identification/data routing, this enables cross-tenant data injection or corruption: attacker-controlled webhook payloads (e.g. fake `orders/create`, `app/uninstalled`, etc.) can be attributed to and processed under a victim shop's tenant scope inside the host application, without any access to the victim's credentials. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app author who follows this gem's documented usage pattern (`data.shop` as tenant key, as shown in `docs/usage/webhooks.md`). The only capability an attacker needs is to be a legitimate, already-installed merchant of the target app (an unprivileged internet user with respect to any other tenant), which is a very low bar, and no secrets or elevated access are required — only the ability to capture and replay one's own valid webhook request with a modified `shop` header.

### Recommendation
Include the shop domain (and other identifying headers such as topic/api-version/webhook-id) in the HMAC-signed material, or independently verify that the shop reported in the header corresponds to a shop the app has previously installed/registered for that specific webhook subscription/session before trusting `request.shop` for tenant routing in `ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata`.

### Proof of Concept
1. App developer installs the app on their own store `attacker-shop.myshopify.com` and registers an `orders/create` webhook handler that uses `data.shop` to route/store data per the documented pattern in `docs/usage/webhooks.md`.
2. Attacker (an ordinary merchant with the app installed) captures a real webhook delivery sent by Shopify to their configured endpoint: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker resends the exact same `B`/`H` pair to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only [6](#0-5) ; it matches `H`, so validation succeeds despite the forged shop header.
5. `WebhookMetadata` is built with `shop: request.shop` returning `"victim-shop.myshopify.com"` [7](#0-6) , and the app's handler processes attacker-controlled data as if it belonged to the victim shop, achieving cross-tenant data injection.

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
