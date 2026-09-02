Confirmed: `Registry.process` validates HMAC only via `Utils::HmacValidator.validate(request)` using `to_signable_string` = `@raw_body`, then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers that are never part of the signed bytes.

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC, allowing cross-tenant webhook spoofing via signature replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` verifies the HMAC exclusively over the raw JSON body [2](#0-1) . However, `Registry.process` trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all parsed from `shopify-*`/`x-shopify-*` HTTP headers — to build the `WebhookMetadata` handed to the app's handler [3](#0-2) . None of these headers are bound to the HMAC signature.

### Finding Description
The binding this gem is supposed to enforce is: `shop that is cryptographically attested == shop the handler acts on`. Instead the code enforces only `raw_body that is cryptographically attested == raw_body parsed`, while `shop` (and `topic`, `webhook_id`, `api_version`) are read unauthenticated from headers:

- `hmac` is computed only from `@raw_body` [4](#0-3) [1](#0-0) .
- `shop`, `topic`, `webhook_id`, `api_version` are all plain header reads with no relationship to the signature [5](#0-4) .
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching, and forwards `request.shop` as ground truth to the handler [3](#0-2) .

Shopify apps share a single `client_secret`/`api_secret_key` across every merchant that installs the app — it is not merchant-specific. A merchant who installs the app (an "unprivileged" actor with respect to *other* tenants) legitimately receives webhooks for their own shop, each with a valid `x-shopify-hmac-sha256` computed over that specific raw body using the app's shared secret. Because the signature covers only the body and not the `shop-domain` header, that same attacker can replay the exact raw body (unmodified, so the HMAC stays valid) to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value (e.g., a victim shop, or any `X-Shopify-Shop-Domain` string the attacker chooses, since it's not itself validated against a trusted domain list) alongside the still-valid HMAC digest. `Registry.process` will not detect anything wrong, since `Utils::HmacValidator.validate` re-derives the digest purely from the (unchanged) body and passes.

### Impact Explanation
This breaks the `shop authenticated == shop the handler acts on` binding for webhook processing, which is a High-severity condition per the rules (scope/tenant-binding check that answers permissively). Any host application that uses `WebhookMetadata#shop` to select which merchant's stored session, access token, or database row to update — the documented and expected usage pattern — can be tricked into applying one shop's legitimately-signed webhook payload against another shop's account context, i.e., cross-tenant data confusion delivered entirely through this gem's own signature-verification logic.

### Likelihood Explanation
Any merchant who installs the app can capture one of their own genuinely-signed webhook deliveries (trivial — they can inspect their own server logs/ngrok tunnel) and replay it with a forged `shop-domain` header. No access token, `client_secret`, or privileged account is required beyond being a normal installer of the app, satisfying the "unprivileged internet user" bar. The exploit needs zero code changes to the raw body, only header substitution, so it is straightforward and repeatable for every webhook topic whose handler trusts `data.shop`.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise all values the handler relies on to route/act on the request) as part of the HMAC-signed bytes in `to_signable_string`, or otherwise cryptographically bind them to the payload before dispatch, rather than reading them unauthenticated from independent headers that sit outside the covered signature.

### Proof of Concept
1. Install the target app as `attacker-shop.myshopify.com`; capture a legitimate webhook delivery, e.g. `orders/create`, with body `RAW_BODY` and header `X-Shopify-Hmac-Sha256: VALID_SIG` (valid because it's signed with the app's single shared `api_secret_key`).
2. Replay the exact same HTTP request to the app's webhook endpoint, keeping `RAW_BODY` and `VALID_SIG` unchanged, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if relevant, forge `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: RAW_BODY, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `RAW_BODY` [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , causing the host application to process attacker-controlled order/webhook data under the victim shop's identity.

### Citations

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
