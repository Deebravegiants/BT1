Confirmed: the webhook `shop` (and `topic`/`webhook_id`/`api_version`) fields are taken from unauthenticated HTTP headers and are not part of the HMAC-signed payload. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook shop-domain header is not covered by HMAC, allowing tenant spoofing of webhook events - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook's HMAC over only the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken straight from unauthenticated HTTP headers when building `WebhookMetadata` passed to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC exclusively over that raw body using the app's single `Context.api_secret_key`. [2](#0-1) [5](#0-4) 

The `shop` accessor, however, is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never included in the HMAC-covered signable string: [6](#0-5) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body authenticity) before forwarding `request.shop` unchanged into `WebhookMetadata`, which the app handler treats as the tenant identifier for the event: [4](#0-3) [7](#0-6) 

Because Shopify apps use a single shared `client_secret` (`api_secret_key`) across all installed shops for HMAC-signed webhooks, the value authenticated by the HMAC is "this body was produced with our app's secret," not "this body belongs to shop X." An unprivileged user who has installed the app on their own shop can capture one of their own genuine webhook deliveries (raw body + valid `X-Shopify-Hmac-Sha256`), then replay that exact byte-for-byte body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it never inspects the shop header, and `Registry.process` hands the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-controlled `body`.

This breaks the intended identity binding: **shop authenticated by HMAC == shop used as the tenant key**. In reality, only "body authenticated by HMAC" is true; the shop is unauthenticated.

### Impact Explanation
Most `shopify_app`/host-application integrations key their per-shop session/access-token lookups and side effects (order sync, data writes, redact/GDPR workflows, etc.) off `data.shop` from `WebhookMetadata`. An attacker can forge events attributed to any victim shop domain (guessable, e.g. `victim.myshopify.com`) with attacker-chosen body content, causing the host app to execute tenant-scoped business logic — including using the victim's stored access token/session — as if the victim's store emitted the event. This is a cross-tenant action performed under the identity of another merchant, without ever needing that merchant's credentials.

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker needs at least one legitimate webhook delivery from their own shop to obtain a valid `(raw_body, hmac)` pair, which is trivially available to anyone who installs the app, and (2) they must know or guess the victim's `myshopify.com` domain, which is generally public/discoverable. No access token, `client_secret`, or privileged account is required — only normal use of the app as an installed, unprivileged merchant.

### Recommendation
Bind the tenant identity into the HMAC-covered material, or otherwise cryptographically verify `shop` before trusting it:
- Include the `shop` (and ideally `topic`/`webhook_id`) in `to_signable_string`, matching it against a value independently verified server-side (e.g. compare against the shop stored for that webhook subscription/session), rather than trusting the header verbatim.
- At minimum, document/enforce that host applications must cross-check `data.shop` against the shop associated with the resource IDs in `data.body` before performing any tenant-scoped action, and validate `data.shop` against the app's session store to ensure a session/install actually exists for that shop.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers including `X-Shopify-Hmac-Sha256: <valid-hmac>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`, and some `raw_body`.
3. Attacker captures this `raw_body` and `X-Shopify-Hmac-Sha256` value (both are attacker-observable since the webhook targets attacker's own endpoint).
4. Attacker sends a new HTTP request to the app's webhook endpoint with the same `raw_body` and same `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request#hmac` is computed via `Digest.hexencode(Base64.decode64(header))`, unchanged from the header value; `to_signable_string` returns the same `raw_body`, so `HmacValidator.validate` succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-22`, `lib/shopify_api/webhooks/request.rb:10-13,35-38`).
6. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body> ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
