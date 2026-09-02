Confirmed: the webhook HMAC validation binds only the raw request body, while the `topic`, `shop-domain`, `webhook-id`, and `api-version` used to route and process the webhook are taken directly from unauthenticated HTTP headers. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook HMAC only binds the request body, letting an unauthenticated `shop-domain`/`topic`/`webhook-id` header spoof the tenant a webhook is attributed to - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (used in `Registry.process`) verifies solely that the body bytes were HMAC-signed by Shopify with `api_secret_key`. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values that `Registry.process` reads off the request and hands to the app's handler as the trusted tenant/topic identity are plain HTTP headers that are never included in the signed material.

### Finding Description
`Request#hmac` is computed from the `x-shopify-hmac-sha256` header and validated against `to_signable_string`, which is defined as just the raw body:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [4](#0-3) 

`Registry.process` only checks this body-only HMAC and then immediately trusts `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` — all sourced from unauthenticated headers via `shopify_header` — to build the `WebhookMetadata` passed to the app's registered handler:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [5](#0-4) 

The equality the library implicitly claims to guarantee is: *"the shop/topic/webhook-id the handler is told about" == "the shop/topic/webhook-id Shopify actually signed for."* Because only the body is signed, this equality does not hold. Any party who can obtain one valid `(raw_body, x-shopify-hmac-sha256)` pair for a given topic (e.g. by receiving a legitimate webhook for a shop they control, or any shop whose webhook payload becomes visible to them) can resubmit that exact body+HMAC to the app's webhook endpoint while freely setting `x-shopify-shop-domain` to any victim shop and `x-shopify-topic`/`x-shopify-webhook-id` to any registered topic/id of their choosing. `Utils::HmacValidator.validate` will still pass because it only re-verifies the (unchanged) body bytes, and the handler will be invoked believing the event legitimately originated from the attacker-chosen shop and topic.

This is the "bytes verified versus bytes parsed"/"shop authenticated versus shop used as identity key" class of bug: the gem verifies body integrity but binds none of the request metadata used downstream for tenant/topic identification to that integrity check.

### Impact Explanation
This breaks the shop/tenant identity binding the webhook system is supposed to provide: the app's webhook handler executes business logic (e.g. `app/uninstalled`, `customers/redact`, order/product mutations) keyed by `data.shop` that is not actually authenticated by Shopify for that shop. An attacker can cause the host application to process a forged event as if it came from any target shop, leading to cross-tenant data confusion (e.g. triggering redaction, uninstall cleanup, or state changes for a shop the attacker doesn't operate) purely by replaying a body+HMAC pair they legitimately obtained elsewhere with a different shop/topic header. This falls under cross-tenant access impact.

### Likelihood Explanation
Any developer or merchant can install the app on their own store (or observe/receive one legitimate webhook delivery, e.g. via app logs, browser devtools on their own storefront, or a compromised/curious insider on one tenant) to obtain a valid body+HMAC pair, then replay it directly to the app's public webhook endpoint with modified `shop-domain`/`topic`/`webhook-id` headers — no access to `api_secret_key`, access tokens, or TLS interception is required, since the attacker is reusing a signature they were legitimately given.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or otherwise cryptographically bind them to the HMAC (e.g., verify them against a value embedded in the payload, or require the host application to separately authenticate the shop before trusting these headers). At minimum, document clearly that `request.shop`/`request.topic`/`request.webhook_id` are NOT covered by the HMAC and must not be treated as verified tenant identity by consuming applications.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (or otherwise obtains one legitimate webhook delivery) and captures a real webhook POST, e.g. for topic `customers/redact`, with raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`).
2. Attacker resends the exact same body `B` and header `H` to the app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: customers/redact` (unchanged, or changed to any topic registered by the app)
   - `x-shopify-webhook-id: <any value>`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`== B`) and matches `H` — validation succeeds.
4. The registered handler for `customers/redact` is invoked with `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)`, causing the app to perform redaction/cleanup logic attributed to `victim-shop.myshopify.com` even though Shopify never generated this event for that shop.

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
