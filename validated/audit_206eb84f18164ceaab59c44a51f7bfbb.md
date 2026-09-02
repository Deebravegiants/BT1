### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not bound to the HMAC signature, allowing cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signable string from the raw HTTP body only, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers and are never included in the HMAC input. `Registry.process` trusts these header-derived values and hands them to the app's `WebhookHandler` as if they were verified, breaking the binding "shop authenticated == shop acted upon."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are parsed straight out of HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e., against the raw body bytes, not the headers: [3](#0-2) 

`Registry.process` validates only this body-scoped HMAC, then constructs `WebhookMetadata` directly from the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` and forwards it to the host app's handler without any additional cross-check between body content and headers: [4](#0-3) [5](#0-4) 

Because Shopify signs webhooks with the app's single shared `client_secret` (`api_secret_key`) — the same secret is used for every shop that installs the app — a valid `(raw_body, hmac)` pair captured from a webhook delivered for one shop remains a **valid signature for that same body under the same secret regardless of which `shop-domain` header accompanies it**. An unprivileged attacker who installs the target app on their own (unprivileged) test shop can legitimately trigger a webhook (e.g. `orders/create`), capture the genuine Shopify-signed `(raw_body, X-Shopify-Hmac-Sha256)` pair, and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop. `Utils::HmacValidator.validate` will still return `true` because it only checks the body against the shared secret; `Registry.process` will then hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

This breaks the equality that should hold: `shop authenticated by HMAC == shop acted upon by the handler`. In this gem, only `body authenticated by HMAC` is guaranteed; `shop` is attacker-controlled request metadata.

### Impact Explanation
Any host application that trusts `WebhookMetadata#shop` (as the gem's own API and its `WebhookHandler` interface encourage) to select or scope per-tenant data can be tricked into performing actions against the wrong shop — including mandatory compliance topics such as `shop/redact` and `customers/redact`, which this gem specifically registers and forwards: [6](#0-5) 
An attacker with only an unprivileged shop can cause the app to execute data-affecting actions (e.g., customer/shop data deletion, order-linked business logic) attributed to a shop they do not control — a cross-tenant impact.

### Likelihood Explanation
Moderate-to-high: the attacker needs no special access beyond installing the app on their own store (a normal, unprivileged action) to obtain a genuinely-signed `(body, hmac)` pair, and needs network access to the app's public webhook endpoint to replay it with a modified `shop-domain` header. No secret key, session, or token theft is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified data, or independently corroborate the header-derived `shop` against an authoritative value extracted from the verified body/other Shopify-guaranteed metadata before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically bound to the signature and must not be trusted for tenant-scoping without additional verification (e.g., cross-checking against the shop that owns the referenced resource ids in the body).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g. creates an order), and captures the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker POSTs the same `B` and `H` to the app's webhook endpoint, replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (unchanged) with the shared `api_secret_key`. [7](#0-6) 
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and performs its action as if it were a genuine event from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
