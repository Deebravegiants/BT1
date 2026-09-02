### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is trusted but not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values that get forwarded to the app's handler as trusted identity are read directly from HTTP headers and are never part of the signed material, since `Request#to_signable_string` only returns `@raw_body` [2](#0-1) . This breaks the intended binding: `shop header == shop the signed payload actually belongs to`.

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field [3](#0-2) . For webhooks, `to_signable_string` is exactly `@raw_body` [4](#0-3) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers with no cryptographic tie to the signature [5](#0-4) .

Crucially, the webhook secret (`Context.api_secret_key`) is the app's single shared secret — the *same* secret is used to sign webhooks for every shop that has installed the app, not a per-shop secret. Any user can freely create a Shopify development store, install the target app, and trigger a real webhook delivery (e.g. by creating an order, updating a product, etc.) to obtain a **genuinely valid `(raw_body, hmac)` pair** signed with the app's real secret, where the body content includes attacker-influenceable data (order/customer/product fields, etc.).

Because `Registry.process` never checks that the `shop-domain` header is the shop that the signature was actually generated for, this attacker can then POST that exact same valid `raw_body` + `hmac-sha256` header directly to the app's public webhook endpoint, only swapping the `shopify-shop-domain` header (and, if desired, `shopify-topic`/`shopify-webhook-id`) to a **different, victim shop's domain**. `HmacValidator.validate` still passes (it only checks the body against the shared secret), and `Registry.process` calls the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [6](#0-5) , attributing attacker-crafted data to the victim shop.

Equality that should hold but does not: `shop header value == shop for which the accompanying signature was actually issued`. Before the request: attacker's own valid webhook has `shop = attacker.myshopify.com`, `hmac = HMAC(secret, body)`. After the attacker's crafted request: `shop = victim.myshopify.com`, `hmac` unchanged and still valid, yet the app treats the payload as authentic data from `victim.myshopify.com`.

Any downstream app logic that keys off `WebhookMetadata#shop` — e.g., looking up the merchant's row by shop domain and applying the payload's contents (order data, customer PII, product changes, `app/uninstalled`/`shop/redact` handling, etc.) — is a cross-tenant data-integrity/confusion vector, entirely reachable by an unprivileged attacker who merely installs the app on their own free store.

### Impact Explanation
This is a cross-tenant boundary violation reachable without any credential, access token, or privileged account — only a free install of the target app on an attacker-controlled shop. It lets the attacker inject falsified webhook events/data attributed to any other merchant of the app, which can corrupt merchant-specific data, trigger unintended actions (e.g. spoofed `shop/redact`, `app/uninstalled`, or order/customer events) against a victim tenant, or leak logic tied to which tenant "sent" the event. This matches the "cross-tenant access" criterion for Critical impact, since the app's identity binding between authenticated bytes (body) and claimed tenant (header) is absent.

### Likelihood Explanation
High. No secrets, tokens or interception are required — an attacker only needs to install the app on their own store (a normal, unprivileged action any internet user can perform for a Shopify app) to obtain a valid signed webhook, then replay it against the public webhook endpoint with a modified `shop-domain` header. The gem provides no additional check that ties the header-derived `shop` to the signed body.

### Recommendation
Bind the shop (and topic) identity to the signed payload rather than trusting unauthenticated headers. Options: include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (this would require a change on Shopify's signing side and is unlikely to be practical), or, more feasibly within this gem, require host applications to cross-check the `shop` header against a known/registered shop for that specific webhook subscription (e.g. verify the shop is one that currently has a valid session/webhook registration in app-managed storage) before trusting `WebhookMetadata#shop`, and document this requirement prominently since the library currently gives no such guidance or enforcement in `Registry.process`.

### Proof of Concept
1. Attacker creates a free Shopify development store and installs the target app; app registers a webhook subscription (e.g. `orders/create`).
2. Attacker triggers a real event (e.g., creates an order with an attacker-chosen note/field) on their own store, causing Shopify to POST a legitimately-signed webhook to the app's endpoint:
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create`
   - Body: attacker-controlled JSON.
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value, then sends a new POST request directly to the app's public webhook endpoint URL with identical body/HMAC but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only validates `raw_body` against the shared `api_secret_key` [7](#0-6) .
5. The registered handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and attacker-controlled body content, even though the data actually originated from the attacker's own store.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
