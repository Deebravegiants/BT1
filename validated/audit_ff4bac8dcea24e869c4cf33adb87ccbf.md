### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the *unauthenticated* `shop-domain` header value to the app's handler as the tenant identifier. This mirrors the DSS `cage` bug class: a value is *used* by downstream logic (routing/attributing data to a shop) that is not actually bound by the cryptographic check that gates the operation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Webhooks::Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, with no cross-check against the HMAC or against any known/installed shop: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` — which, per `HmacValidator#validate_signature`, recomputes the HMAC over `to_signable_string` (i.e., only the body) and compares it to the `hmac-sha256` header — and then immediately forwards `request.shop` (untouched by the HMAC check) into `WebhookMetadata`, which is handed to the app's handler as the tenant identity: [3](#0-2) [4](#0-3) 

The documented handler contract explicitly tells app authors to trust `data.shop` as "The shop domain of the webhook" and to key their own persistence/queueing logic on it: [5](#0-4) 

The equality this code implicitly assumes is:
`shop authenticated by HMAC == shop delivered to the handler (data.shop)`

In reality, the HMAC only proves "the body bytes were produced with the app's `client_secret`" — it says nothing about which shop the header claims to be from. Any party that can obtain one genuine `(body, hmac)` pair signed with the app's secret (e.g., a merchant who has installed the multi-tenant app and receives their own legitimate webhooks) can resend that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still pass (it never looks at the shop header), and `Registry.process` will invoke the handler with `data.shop` set to the attacker-chosen value alongside the replayed body.

### Impact Explanation
This breaks the tenant boundary the library is trusted to establish: an authenticated webhook-processing path can be made to attribute one tenant's payload to a different tenant identifier. Depending on how the host app persists webhook data (the documented pattern is to key storage directly off `data.shop`, e.g. `perform_later(shop_domain: data.shop, ...)`), this enables cross-tenant data injection/confusion — writing or triggering side effects against another merchant's records using a replayed, self-authenticated payload. This falls under the "cross-tenant access" Critical impact category, since the authentication mechanism (HMAC) does not bind the identity field (`shop`) that downstream logic relies on for tenant isolation.

### Likelihood Explanation
Exploitation requires the attacker to already be a legitimate installer of the same multi-tenant app (to obtain a validly-signed `(body, hmac)` pair from their own store's real webhook deliveries), then replay it against the same endpoint with a forged `shopify-shop-domain` header. This is a realistic scenario for any SaaS app built on this gem that serves multiple merchants, since the attacker only needs their own tenant account — no access to the app's `client_secret` or another merchant's credentials is required.

### Recommendation
Either include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material used for verification, or have `Registry.process`/`HmacValidator` cross-check `request.shop` against the shop associated with the app installation *before* invoking the handler, rather than passing the raw, unauthenticated header value through unchanged. At minimum, document prominently that `data.shop` in the webhook handler is not authenticated by the HMAC and must be independently validated by the host app against known/installed shops before being trusted for tenant-scoped operations.

### Proof of Concept
1. App A (built on this gem) is installed by two independent merchants: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`.
2. Shopify sends `attacker-shop` a legitimate webhook: body `B`, header `shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(App A's client_secret, B)`), and `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and replays it to App A's webhook endpoint, keeping body `B` and header `H` identical but changing `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and finds it equals `H` — validation passes because the shop header was never part of the signed input: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, causing the app to process/store the attacker's payload under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L12-29)
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
