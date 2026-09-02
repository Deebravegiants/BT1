## Title
Webhook `shop`/`topic`/`webhook-id` identity fields are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the **raw body only**, while `ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, and `webhook_id` values taken straight from HTTP headers — none of which are covered by the HMAC check. This breaks the identity binding `hmac == HMAC(secret, body ‖ shop ‖ topic)` that a webhook consumer must rely on, allowing a party who can obtain any one valid `(body, hmac)` pair for the shared app `client_secret` to replay it with a forged `shop` header and have it processed as if it originated from a different, victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, and `webhook_id` are read verbatim from attacker-controllable HTTP headers with no cryptographic tie to the signature: [2](#0-1) 

`Registry.process` validates only that HMAC, then immediately trusts those unauthenticated header values to construct the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms the same: it only ever signs `verifiable_query.to_signable_string`, i.e. the body, never the headers: [4](#0-3) 

Because the same app `client_secret` (`api_secret_key`) is used to sign webhooks for **every shop** that installs the app, any unprivileged user who installs the app on a store they control (e.g. a free development store) can trigger a real webhook delivery and capture a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with that shared secret. That pair can then be replayed to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain — the equality `shop_verified_by_hmac == shop_acted_upon` never holds, yet the request passes `HmacValidator.validate` and is dispatched to the handler labeled with the victim's shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the field the handler acts on (`shop`, and also `topic`/`webhook_id`) is never bound to the cryptographic proof of authenticity. In a multi-tenant SaaS app built on this gem, an attacker-controlled webhook body can be attributed to an arbitrary victim shop, letting the attacker inject fabricated events (e.g. fake `orders/create`, `app/uninstalled`, `customers/data_request`) into another tenant's processing pipeline. Depending on what the host app does with `WebhookMetadata#shop` (commonly: looking up that shop's session/access token, triggering per-tenant business logic, or de-provisioning), this can lead to cross-tenant data corruption or unauthorized actions performed under another merchant's identity — a Critical-severity cross-tenant access impact.

### Likelihood Explanation
Any user can freely create a Shopify development/trial store and install the app to receive genuinely-signed webhooks for that store — no special privilege or credential theft is required, since `Registry.process` and `HmacValidator.validate` never re-derive or check the headers against the signature.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable payload (or independently verify them against a value looked up from a trusted, authenticated source, e.g. the app's own session store), so that the HMAC binds the identity fields the handler acts on, not just the raw body.

### Proof of Concept
1. Attacker installs the target app on their own Shopify development store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g. `orders/create`) and captures the request: `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac>` — both valid because they're signed with the app's shared `client_secret`.
3. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker_controlled_body, ...)` and processes attacker-supplied data as though it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
