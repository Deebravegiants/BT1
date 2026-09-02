Confirmed: `to_signable_string` in `Webhooks::Request` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers via `shopify_header` and are never included in the HMAC-signed content. [1](#0-0) [2](#0-1) 

### Title
Webhook tenant identity (`shop-domain` header) is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` (and `topic`/`webhook_id`) values used to attribute the webhook to a specific merchant/tenant are read from unauthenticated HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`) that are never part of the signed content (`to_signable_string` returns only `@raw_body`). This breaks the identity binding `verified_bytes == attributed_tenant`: the bytes covered by the HMAC (body only) are not equal to the bytes actually used to decide "which shop does this event belong to" (the `shop-domain` header).

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it with the `hmac` field using `OpenSSL.secure_compare`. For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body`, and `hmac` is read from the `hmac-sha256` header. [3](#0-2) 

Separately, `shop`, `topic`, and `webhook_id` are extracted directly from headers with no cryptographic binding to the body or to the HMAC: [4](#0-3) 

`Registry.process` validates only the body HMAC and then immediately trusts `request.shop` and `request.topic` to dispatch and populate `WebhookMetadata`, which the host application uses to attribute the event to a tenant/shop record: [5](#0-4) 

Because the shared `api_secret_key` used to compute the HMAC is the same across every shop that has installed a given app (it is per-app, not per-shop), any merchant who has legitimately installed the app can capture one of their own genuine `(raw_body, hmac)` pairs and replay it to the app's webhook endpoint with an arbitrary, attacker-chosen `shopify-shop-domain` header. The HMAC check still passes because the signature never covered the shop identity, only the body bytes — yet the host application, following this gem's documented `WebhookMetadata` API, will process the request as if it originated from the spoofed shop.

### Impact Explanation
This breaks the tenant boundary that the HMAC is supposed to enforce: an attacker (any merchant who has installed the target app) can forge webhook events that this gem attributes to a shop they do not control, since `request.shop` is unauthenticated and is the value handed to application handlers as the source of truth for which tenant the event belongs to. Depending on how the host app keys off `WebhookMetadata#shop` (e.g., to look up a merchant record, decrement/credit balances, mark orders, or write shop-scoped data), this enables cross-tenant data manipulation — the impact class explicitly listed as Critical (cross-tenant access) in the rules.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate, unprivileged merchant who has installed the target app (no special privilege, no access token or secret key needed) — they always receive at least one genuine `(body, hmac)` pair from real Shopify webhook traffic to their own installation, since the HMAC secret is shared per-app across all installs. Replaying that pair with a modified `shop-domain` header to the app's public webhook endpoint requires no interaction with Shopify's systems at all.

### Recommendation
Bind the shop identity into the verified material: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (which would require a change in what Shopify signs) — since that's Shopify-side, at minimum this gem should not expose `request.shop` as trustworthy without also requiring/encouraging the host application to cross-check the header-derived shop against a shop the app actually has an active session/install for before treating the payload as belonging to that shop, and the docs/`WebhookMetadata` API should clearly document that `shop` is unauthenticated header data, not verified by the HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B` and header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's shared `api_secret_key`), along with `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and hmac header `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only (`to_signable_string`) — identical to `B` — so validation succeeds. [6](#0-5) 

4. `request.shop` returns `"victim.myshopify.com"` from the forged header, and the handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the host application to process/attribute the (attacker-controlled) event data as belonging to the victim tenant.

### Citations

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
