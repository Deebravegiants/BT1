This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only the HMAC over the request and then forwards `request.shop` (the unsigned header) directly into `WebhookMetadata` for the app's handler [3](#0-2) .

### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing via webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body alone, never binding the `shop-domain` header that `Registry.process` later trusts as the tenant identity passed to the app's webhook handler.

### Finding Description
`HmacValidator.validate` accepts any `VerifiableQuery` and checks `hmac` against `HMAC-SHA256(secret, to_signable_string)` [4](#0-3) . For webhooks, `to_signable_string` is defined as `@raw_body` only [1](#0-0) , while `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is entirely separate from the signed bytes [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` and then constructs `WebhookMetadata` using `request.shop` taken straight from that unauthenticated header [5](#0-4) .

This breaks the intended binding `shop_authenticated == shop_delivered_to_handler`. Because an app's webhook `api_secret_key` is shared across all merchants/shops installed on that app (it is not per-shop), any shop that legitimately receives a real webhook from Shopify (a valid `raw_body` + `hmac`) possesses a `(body, hmac)` pair that remains cryptographically valid for that same secret regardless of which shop-domain header accompanies it. An unprivileged holder of one such legitimate webhook delivery can replay the identical `raw_body`/`hmac-sha256` bytes to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim shop). `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` forwards the attacker-chosen shop value to the handler as if it were authenticated.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem authenticates the webhook payload's integrity but hands the host application an unauthenticated tenant identifier (`shop`) that host applications reasonably assume is bound to the same HMAC-verified request (mirroring Shopify's own guidance that the shop header is part of the trusted webhook context). Host apps that key session/access-token lookups, feature toggles, or data mutations off `WebhookMetadata#shop` can be made to attribute attacker-controlled webhook bodies to a different, victim tenant, resulting in cross-tenant data confusion — a High/Critical-class impact per the crossing of an identity boundary this gem was expected to enforce.

### Likelihood Explanation
Any user who is an installed merchant of the target app can capture one legitimate webhook delivery Shopify sends to them (valid body+HMAC under the app's shared secret) and replay it against the public webhook endpoint with a forged `shop-domain` header pointing at another shop — no access to `api_secret_key`, tokens, or privileged access is required, only observation of one's own webhook traffic and the ability to send an HTTP request to the app's publicly reachable webhook callback.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signable content, or otherwise cryptographically bind the `shop-domain` header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that consumers must independently verify `request.shop` against the shop that is expected to own the subscription/topic before acting on it.

### Proof of Concept
1. App installs on `victim-shop.myshopify.com`; attacker installs the same app on `attacker-shop.myshopify.com`.
2. Shopify sends attacker a legitimate webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` under the app's single shared `api_secret_key`), header `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker POSTs the same `B` and `H` to the app's public webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`= B`) and matches `H` — validation passes [6](#0-5) .
5. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop = "victim-shop.myshopify.com"` taken from the attacker-controlled header [7](#0-6) , and the host app's handler executes tenant-scoped logic believing it originated from `victim-shop`.

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
