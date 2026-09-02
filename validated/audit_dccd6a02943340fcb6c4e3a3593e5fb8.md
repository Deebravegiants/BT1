The webhook HMAC validation only signs the raw body — not the `shop` (or `topic`/`webhook_id`) header — yet the unauthenticated `shop` header value is exactly what gets forwarded to the app's webhook handler as the tenant identity.Confirmed: `ShopifyAPI::Webhooks::Registry.process` validates only `Utils::HmacValidator.validate(request)`, which signs/verifies `request.to_signable_string` = `@raw_body` alone [1](#0-0) . The `shop`, `topic`, and `webhook_id` values that get forwarded to the merchant's registered handler are all pulled straight from HTTP headers that are never part of the signed content [2](#0-1) .

### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Registry.process` validates the HMAC exclusively against that body. The `shop` (tenant identity), `topic`, and `webhook_id` values used downstream come from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) that are not covered by the signature at all.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` is the entry point host applications call to handle incoming webhooks:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes an HMAC-SHA256 over `verifiable_query.to_signable_string` using the app's single `api_secret_key`, and compares it to the signature supplied in the `hmac-sha256` header: [3](#0-2) 

For `Webhooks::Request`, `to_signable_string` is defined as just the raw body — `shop`, `topic`, `api_version`, and `webhook_id` are excluded from the signed material:

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [4](#0-3) 

Because a single app has one `api_secret_key` shared across every shop that installs it, a valid HMAC over a given body only proves "this body was signed by Shopify for this app" — it proves nothing about which shop the body belongs to. The equality the code implicitly assumes but never enforces is:

`shop_that_signed(raw_body) == shop_header_value`

but only `hmac_header == HMAC(api_secret_key, raw_body)` is actually checked; `shop_header_value` is accepted unconditionally and handed to the handler as `WebhookMetadata#shop`.

An attacker who legitimately installs the app on their own shop receives real, validly-signed webhook deliveries for that shop (body + `hmac-sha256` + `shopify-shop-domain: attacker-shop.myshopify.com`). Because the signature covers only the body, the attacker can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting `shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` still passes (body and secret are unchanged), so `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, causing the host application to attribute/process the attacker's data as if it originated from the victim shop — a cross-tenant data-integrity breach reachable by any unprivileged internet user who has (or once had) a legitimate install of the app.

### Impact Explanation
This breaks tenant isolation: any app built on this gem's webhook handling attributes incoming webhook payloads to whichever shop the request header claims, with no cryptographic binding between the signed body and that claim. An attacker-controlled shop can inject data (order/customer/app-uninstalled events, etc., depending on what handlers do with the payload) tagged as belonging to a different merchant's shop, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The only prerequisite is that the attacker has (or had) a legitimate install of the target app on any shop — a normal, unprivileged action available to any internet user who can install a public Shopify app. No access to `api_secret_key`, access tokens, or TLS interception is required; the attacker only replays their own genuinely-signed webhook body with a modified `shop` header value.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed/verified material (e.g., compare them against values obtained via a separate authenticated channel, or require the host application to look up the expected shop's own secret and re-derive/compare), or otherwise cryptographically bind the header-derived tenant identity to the HMAC-covered body so that `to_signable_string` cannot validate against a body originally issued for a different shop.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify delivers a legitimate webhook: body `B`, header `shopify-hmac-sha256: H = HMAC(api_secret_key, B)`, header `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures this request (they own the shop and can freely trigger/observe its own webhooks, e.g. via order creation).
3. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and same `shopify-hmac-sha256: H`, but `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B) == H` → true [5](#0-4) .
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [6](#0-5)  — the host application now processes attacker-supplied data under the victim shop's identity.

### Citations

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
