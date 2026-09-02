## Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain` header that the gem exposes as `request.shop` and passes into `WebhookMetadata#shop`. Because `Utils::HmacValidator.validate` verifies only what `to_signable_string` returns, an attacker can take a body+HMAC pair legitimately produced for one shop (e.g., their own store, since the app's `client_secret` used to sign webhooks is shared across every shop that installs the app) and replay it against a target app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header. The forged shop attribution still passes HMAC validation and is delivered to the app's handler as trusted data.

## Finding Description
`Request#to_signable_string` only signs `@raw_body`: [1](#0-0) 

`Request#shop` is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` only checks the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., only the body) — it never validates the `shop` header — and then forwards `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as authoritative tenant identity: [3](#0-2) [4](#0-3) 

The gem's own documentation instructs implementers to key downstream, per-tenant processing directly off this unauthenticated field: [5](#0-4) 

The equality that is expected to hold is: *shop attributed to the webhook == shop that actually produced the signed body*. Because `shop` is excluded from the signed material, an attacker who controls the `x-shopify-shop-domain` header can break that binding while keeping a cryptographically valid signature, since the app's `client_secret` (and hence the HMAC key) is identical for every shop that installs the app — not per-shop.

## Impact Explanation
An unprivileged internet user who has installed the target app on their own (attacker-controlled) shop can obtain a legitimately-signed webhook body/HMAC pair from Shopify for their own shop, then POST that exact body/HMAC directly to the app's public webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Registry.process` will validate successfully and hand the handler `WebhookMetadata` claiming the data belongs to the victim shop. Any app that follows the documented pattern (persisting/queuing data keyed by `data.shop`) will ingest attacker-controlled data under another merchant's tenant, i.e. cross-tenant data injection/confusion — crossing the tenant boundary this gem is meant to enforce for webhook processing.

## Likelihood Explanation
Exploitation requires only: (1) the attacker installs the target app on any shop they control (a normal, unprivileged action, e.g. a free Shopify dev/partner store) to obtain one valid signed webhook, and (2) the attacker sends a crafted HTTP POST directly to the app's public webhook URL with a forged `shop-domain` header. No access to the app's `client_secret`, access tokens, or any other shop's credentials is required.

## Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`/`api_version`) header values in the signed material used by `to_signable_string`, or otherwise cryptographically bind the shop domain to the signature (Shopify does not currently sign headers, so the safer fix is for the gem to independently verify `request.shop` against a shop that is expected to receive this topic, e.g. by requiring callers to pass an expected/known shop list, or by treating `data.shop` as untrusted and cross-checking it against the shop associated with the webhook's stored subscription/session before using it as a tenant key).

## Proof of Concept
1. Install the vulnerable app on `attacker.myshopify.com` and let it register for a webhook topic (e.g. `orders/create`).
2. Capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — this HMAC key is the same for all shops using the app.
3. Send a forged request directly to the app's public webhook endpoint:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: H
   x-shopify-shop-domain: victim.myshopify.com
   Body: B
   ```
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) verifies `H` against `B` and succeeds, since `shop` is never part of `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's own webhook body>, ...)`, causing the app to process/store attacker-controlled data under the victim shop's tenant.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
