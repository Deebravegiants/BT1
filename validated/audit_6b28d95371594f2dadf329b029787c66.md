### Title
Webhook `shop` tenant identity is unauthenticated and not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, but the `shop` (tenant identity) is read from an unauthenticated HTTP header and is never included in the signed material. `Webhooks::Registry.process` validates the HMAC and then hands the handler `request.shop` as the trusted tenant identifier, so the equality the library implicitly claims — "HMAC-valid request" == "request genuinely originated for `request.shop`" — does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — it never touches `shop`: [3](#0-2) 

`Registry.process` validates only the HMAC and then trusts `request.shop` (and `request.webhook_id`, `request.topic`) verbatim when constructing `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because a single app has one `api_secret_key` shared across **every** shop that installs it (it is the app's client secret, not a per-shop key), the HMAC over the body is identical no matter which shop originally produced it. The `shop-domain` header is not part of the signed payload, so:

`HMAC_valid(body, secret) == HMAC_valid(body, secret)` regardless of `shop header value`

i.e. `shop_claimed_by_request != shop_that_actually_produced(body, hmac)` can be true while `HmacValidator.validate` still returns `true`.

### Impact Explanation
Any unprivileged internet user who installs the target app on their own (even free/development) Shopify store is a legitimate webhook counterparty for that app. That user can:
1. Trigger a real webhook delivery for their own shop (e.g. `orders/create`), capturing the genuine `raw_body` and its valid `x-shopify-hmac-sha256` value.
2. Replay that exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it only checks the body), `Registry.process` proceeds, and the handler receives `WebhookMetadata` claiming `shop: <victim-domain>` with attacker-controlled `body`.

Depending on how the host application uses `data.shop` to scope database writes, trigger shop-scoped side effects, or select the access token/session to act with, this allows cross-tenant data injection/corruption — attacker-controlled webhook content is attributed to and processed under a victim tenant's identity. This satisfies the "Critical: cross-tenant access" impact bucket, since it breaks the shop-tenant isolation this gem is meant to enforce for webhook processing, without requiring `api_secret_key`, an access token, or any privileged account — only becoming an ordinary merchant/installer of the app.

### Likelihood Explanation
High. The prerequisite is only that the attacker can install (or already has installed) the target app on any shop they control — a normal, unprivileged interaction with no special credentials needed — and can capture one legitimate webhook delivery to their own endpoint/proxy. Constructing and sending the replayed HTTP POST with a modified header requires no cryptographic material at all, since `shop` is never part of the signed content.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically verify it:
- Include `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) in `Request#to_signable_string` so the HMAC covers the full identity tuple, not just the body; or
- Have `Registry.process` cross-check `request.shop` against the shop associated with the resolved handler/session context (e.g., require the caller to pass an expected shop and assert equality) before dispatching; or
- At minimum, document/enforce that host applications must independently re-verify `shop` against their own installed-shop registry before trusting `WebhookMetadata#shop`, since the library's own HMAC check does not protect that field today.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Attacker triggers a webhook subscribed by the app (e.g. creates an order), and captures the raw POST sent to the app's webhook endpoint, including headers:
   - `x-shopify-hmac-sha256: <valid-hmac-for-raw-body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - body: `<raw_body>`
3. Attacker replays the identical HTTP POST to the same endpoint, keeping `x-shopify-hmac-sha256` and body unchanged, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. On the server, `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`@raw_body`) — this still matches, since the body and secret are unchanged. [4](#0-3) 
5. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)`, even though `victim-shop.myshopify.com` never sent this webhook.

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
