### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` only returns the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are all read from unauthenticated HTTP headers, are never included in the signed material. `Registry.process` verifies only that the body's HMAC is valid, then hands the attacker-controlled `shop` header straight to the app's webhook handler as the tenant identity for that event.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are entirely outside the signature: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop`, `request.topic`, etc. without any additional binding to the body or to the secret: [3](#0-2) 

The identity-binding equality that should hold is:

`shop that HMAC authenticates == shop delivered to the handler as data.shop`

but the actual equality enforced is only:

`HMAC(raw_body) == signature`

with `shop` (and `topic`/`webhook_id`) completely decoupled from that check. Because HMAC-SHA256 of a Shopify webhook body only depends on the app's `client_secret` and the body bytes — not on which shop sent it — any request whose body+HMAC pair was legitimately generated for *any* shop using the same app's secret (including a store the attacker legitimately owns) remains valid regardless of the `shop-domain` header value attached to the replay.

### Impact Explanation
An unprivileged attacker who owns any store that has this app installed (e.g., a free development store) can trigger a real webhook for their own shop, capture the valid `raw_body` + `X-Shopify-Hmac-Sha256` pair (a completely legitimate, unprivileged action against their own tenant), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim shop, or a shop domain the attacker doesn't control at all). `Registry.process` validates the HMAC successfully (it only checks the body) and passes `request.shop` — now attacker-chosen — into `WebhookMetadata` for the handler: [4](#0-3) 

Any host application that uses `data.shop` to key session lookups, write to per-shop records, or gate mandatory-compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) will process the event under an attacker-controlled tenant identity, i.e., cross-tenant data injection/confusion.

### Likelihood Explanation
Likelihood is high for any consumer of this gem's documented `Registry.process` API: it requires no secret, no access token, and no interaction with the target tenant — only that the attacker has (or creates) a store where the target app is installed, which is a normal unprivileged action. The header-spoofing step is trivial HTTP request manipulation.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material verified against the HMAC, or otherwise cryptographically bind the shop-domain header to the specific webhook delivery (e.g., cross-check it against a store list retrieved via an authenticated API call, or require the host app to independently validate `shop` against its own session store before trusting `data.shop`). At minimum, document prominently that `data.shop` is unauthenticated header data and must never be trusted for tenant attribution without independent verification.

### Proof of Concept
1. Attacker installs the target app on their own (or any accessible) Shopify store, `attacker-shop.myshopify.com`.
2. Attacker triggers a real webhook for a registered topic (e.g., `orders/create`) on their store and captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` header sent by Shopify to the app's webhook endpoint.
3. Attacker replays an HTTP POST to the same webhook endpoint with:
   - Body: identical `raw_body` (unmodified, so HMAC still matches)
   - Header: `X-Shopify-Hmac-Sha256`: unchanged (still valid for this body)
   - Header: `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (or any string)
4. `Registry.process` computes `Utils::HmacValidator.validate(request)` → `true`, because `to_signable_string` for the webhook request only covers `raw_body`.
5. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though this data actually originated from `attacker-shop.myshopify.com`.

### Citations

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
