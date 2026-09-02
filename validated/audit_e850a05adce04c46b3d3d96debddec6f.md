## Title
Webhook Processing Trusts Unauthenticated `shop` Header Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw request body against the HMAC signature, but then hands the caller-supplied `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — none of which are covered by that signature — straight to the app's handler as trusted tenant-identifying data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body wasn't tampered with) and then immediately constructs `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id`: [3](#0-2) 

`HmacValidator.validate` computes the signature using `Context.api_secret_key`, the app's single `client_secret`, which is shared across every shop that has installed the app — it is not per-tenant: [4](#0-3) 

The identity binding that is broken: `HMAC-covered bytes (body only) != tenant-identifying data (shop header) trusted by the handler`. Because the HMAC secret is shared across all installations of the app, any merchant who has installed the app can legitimately trigger a webhook to obtain a body + valid HMAC pair signed with the app's shared secret, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. The signature still validates (it only checks the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen value — attributing the event to a shop the attacker does not control.

### Impact Explanation
This lets an unprivileged internet user (any merchant who has installed the shared app) forge webhook events that a host application will process as belonging to a different tenant, i.e. cross-tenant access: any app logic keyed off `WebhookMetadata#shop` (data updates, entitlement changes, GDPR/compliance actions, resource lookups scoped "by shop") can be triggered under a victim shop's identity using only the attacker's own legitimately-issued webhook material.

### Likelihood Explanation
Requires only: (1) installing the target app on any shop the attacker controls (a normal, unprivileged action), (2) capturing one webhook delivery for that shop, and (3) resending it with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged access is needed — the shared `api_secret_key` used to compute/verify the HMAC is exactly what makes the replayed signature valid regardless of which shop is named in the headers.

### Recommendation
Bind the tenant-identifying headers into the HMAC-verified surface: either include `shop`, `topic`, and `webhook_id` in the signable string, or independently corroborate `request.shop` against a value obtained through an authenticated channel (e.g. reconcile against the shop recorded when the webhook subscription was registered) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and provokes any webhook (e.g. `orders/create`), capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed with the app's shared `api_secret_key`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and performs whatever tenant-scoped action the app implements for that webhook, now misattributed to the victim shop.

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
