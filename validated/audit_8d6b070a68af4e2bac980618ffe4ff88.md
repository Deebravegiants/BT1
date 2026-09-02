### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` (and `topic`) HTTP headers — which are never included in the signed bytes — to determine which tenant the webhook belongs to and to route/execute the handler. This breaks the identity binding: `bytes verified (raw body)` ≠ `bytes used to establish shop identity (unauthenticated header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC over the `Request` object (i.e. only over the body) and then immediately trusts `request.shop` and `request.topic` (header values) to select the handler and construct the `WebhookMetadata` that is handed to the app's business logic as the authoritative tenant identifier: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no additional verification step: [4](#0-3) 

Critically, the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across **every shop that has the app installed** — it is not per-tenant. Any shop that installs the app receives genuine, validly-signed webhooks from Shopify for its own store events. Because the signature never binds the `shop-domain` header (or `topic`/`webhook-id`) to the body, an attacker who controls one installed shop can take a legitimately-signed payload (received on their own tenant) and resend it to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` header value. `HmacValidator.validate` will still pass, because it only recomputes the HMAC over the identical raw body: [5](#0-4) 

The equality that should hold but does not: `shop_bound_by_hmac == shop_used_to_identify_tenant`. In this gem, the left side is undefined (HMAC covers no shop identifier at all), while the right side is taken verbatim from an attacker-controllable header.

### Impact Explanation
This is a cross-tenant identity-binding break: an app relying on `Registry.process` / `WebhookMetadata#shop` (the gem's documented mechanism for webhook processing, see `docs/usage/webhooks.md`) to determine which merchant's data a webhook body applies to can be made to act on data intended for tenant A while attributing it to victim tenant B, or vice versa. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up the merchant record to update, to select the session/access token to use for follow-up API calls, or to gate data writes), this enables cross-tenant data corruption/impersonation — satisfying the Critical "cross-tenant access" impact category. No leaked credentials, TLS interception, or possession of `api_secret_key` are required: the attacker only needs to be a legitimate (even free/trial) installer of the app on their own store, which is an ordinary "unprivileged internet user" action relative to other tenants of the app.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that installs the app on more than one shop (i.e., any real multi-tenant SaaS app built on this gem). The only requirements are: (1) the attacker installs the app on a shop they control (normal, unauthenticated-relative-to-victim action), (2) they trigger or wait for any webhook topic they've subscribed to, and (3) they replay the body with a different `shop-domain` header to the same public webhook endpoint. No special network position or secret material beyond what any installer already legitimately receives is needed.

### Recommendation
- Include the tenant-identifying fields (`shop-domain`, `topic`, and ideally `webhook-id`) inside the HMAC-signed payload check, or cross-verify them against Shopify's request source (e.g., validate the shop domain against a known, previously-recorded value tied to the specific webhook subscription/session, not just trust the header).
- Alternatively, bind webhook processing to a per-registration secret/subscription id rather than relying solely on the shared app secret plus an unauthenticated header for tenant attribution.
- Document clearly (and enforce in `Registry.process`) that consuming apps must independently verify `WebhookMetadata#shop` is a shop actually associated with a prior OAuth installation for that specific webhook subscription before acting on it.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate self-service installation).
2. Attacker triggers a webhook event on their own shop (e.g., updates a product) and captures the resulting POST to the app's webhook endpoint, including the genuine `X-Shopify-Hmac-Sha256` header and raw body — both signed with the app's single shared `client_secret`.
3. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only recomputes the signature over `@raw_body`, which is unchanged: [3](#0-2) 
5. `Registry.process` dispatches to the registered handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop — the app now processes attacker-controlled data under the victim tenant's identity.

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
