### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) headers are trusted but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then forwards these unverified header-derived values (in particular `shop`) to the app's `WebhookHandler` as if they were as trustworthy as the signed body.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Whereas `shop`, `topic`, `api_version`, and `webhook_id` are parsed straight from headers, entirely outside the HMAC computation: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e. only the body) and then uses `request.shop`, `request.topic`, `request.api_version`, `request.webhook_id` unconditionally to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

This breaks the identity binding: `bytes verified (raw_body signed with shared api_secret_key) != shop asserted (header value trusted by handler)`. By contrast, the OAuth callback path (`AuthQuery`) correctly includes `shop` inside the signable string that is HMAC-verified: [5](#0-4) 

The `api_secret_key` (app `client_secret`) used to compute/verify the webhook HMAC is shared across every shop that installs the app — it is not shop-specific. This means any merchant who installs the app receives real, validly-signed webhook deliveries for their own shop (a legitimate, unprivileged action requiring no special access). Such a merchant can capture one of these deliveries (raw body + valid `x-shopify-hmac-sha256`) and replay it to the app's webhook endpoint while altering only the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header to name a different, victim shop that also uses the same app. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) will still pass because it only checks the raw body against the shared secret: [6](#0-5) 

The handler then receives `WebhookMetadata` attributing the (attacker-controlled) body to the victim's shop, exactly mirroring the report's rounding/inflation pattern of "the value verified is not the value acted upon" — here the field acted on (`shop`) is not part of the HMAC input at all.

### Impact Explanation
Any app built on this gem that uses the `shop` field from `WebhookMetadata` to decide which tenant's records to create/update/delete (a documented and expected usage pattern, since `WebhookMetadata#shop` is the only per-request tenant identifier the gem exposes for webhook processing) can be tricked into applying attacker-supplied webhook payloads to another merchant's tenant. This is a cross-tenant data integrity/confidentiality violation triggered purely by forging an HTTP header, without needing the victim's access token or the app's `client_secret` — only participation in the app as any other installed merchant.

### Likelihood Explanation
High. No special privileges, tokens, or social engineering are required beyond being any unprivileged merchant who has installed the target app (or in some deployments, simply obtaining any single valid signed webhook body/HMAC pair, since the secret is shared and the signature covers only the body, not the shop). Forging the `x-shopify-shop-domain` header on an HTTP POST is trivial.

### Recommendation
Include the shop domain (and topic/webhook id, if they are relied upon for handler dispatch/business logic) inside the HMAC-signed content, or otherwise cryptographically bind the header-derived `shop` to the verified body before constructing `WebhookMetadata`. At minimum, update `Request#to_signable_string` to incorporate the `shop-domain` header value (consistent with how `AuthQuery#to_signable_string` includes `shop`), and document that `WebhookMetadata#shop` is only trustworthy after this binding is enforced.

### Proof of Concept
1. App `A` shares one `client_secret` across all installed shops.
2. Attacker installs `A` on their own shop `attacker.myshopify.com` and triggers any webhook event (e.g., `orders/create`), capturing the POST body and the valid `x-shopify-hmac-sha256` header Shopify sent.
3. Attacker replays the exact same request to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (a different shop that also has `A` installed).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `request.shop == "victim.myshopify.com"`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the shared secret — the shop header was never part of the signed input.
6. The app's `WebhookHandler#handle` receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: attacker_body, ...)` and processes the attacker's payload as if it originated from the victim's shop.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
