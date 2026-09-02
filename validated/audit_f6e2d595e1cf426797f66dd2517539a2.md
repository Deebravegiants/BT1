### Title
Webhook Shop-Domain Spoofing via Cross-Tenant HMAC Replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `ShopifyAPI::Webhooks::Registry.process` verifies the webhook's authenticity solely against that raw body via `Utils::HmacValidator.validate`. The `shop-domain` header — the value that identifies *which tenant* the webhook belongs to and that is handed unmodified to the app's handler as `data.shop` — is never included in the signed content. An attacker who legitimately receives one genuinely-signed webhook (e.g. from their own Shopify store where they installed the app) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the signature check still passes.

### Finding Description
The identity binding that should hold is:
`shop header used by the handler == shop that Shopify actually generated/signed this payload for`

but the gem only enforces:
`HMAC(raw_body, api_secret_key) == received_hmac`

The `shop` field is never part of the signed data: [1](#0-0) 

`Registry.process` validates the HMAC over the request as a `VerifiableQuery`, then immediately trusts `request.shop` to build the metadata passed to the handler: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the raw body) against the computed signature — it has no notion of the `shop` header at all: [3](#0-2) 

Because the app's `api_secret_key` is shared across every merchant that installs the app (it is not per-shop), any merchant who installs the app can obtain a webhook whose body+HMAC pair is valid under that shared secret. That attacker-controlled request (same body, same valid HMAC) can then be re-sent to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to a victim shop's domain. The signature validation in `Registry.process` still succeeds because it never checked the header, and the handler receives `WebhookMetadata` claiming the event is for the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding that host applications rely on (the docs explicitly instruct developers to key business logic off `data.shop`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, see `docs/usage/webhooks.md`). An attacker with their own (attacker-controlled) shop install can forge webhooks that the app processes as belonging to a different, victim tenant — e.g., triggering `app/uninstalled` handling that deletes or resets a victim shop's stored session/data, or feeding attacker-controlled `body` content into logic keyed to the victim's shop record. This is a cross-tenant access/confusion vulnerability stemming from the gem's own HMAC verification scope.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the app on their own Shopify store (or otherwise causes it to send them a genuine webhook, which is normal, permitted usage for any developer/merchant), (2) capture of one valid raw_body + `hmac-sha256` header pair, and (3) replaying that HTTP POST to the app's public webhook endpoint with a modified shop-domain header. No access to the app's `api_secret_key`, access tokens, or any privileged credential is needed — this is achievable by any unprivileged internet user who can install the target app on a store they control.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header into the value that is verified, or otherwise cross-check the header-derived shop against a stored per-shop webhook registration/secret before trusting `request.shop` in `Registry.process`. At minimum, document that `data.shop` from `WebhookMetadata` is not cryptographically bound to the signed payload and must not be used as the sole tenant-identification mechanism for sensitive operations.

### Proof of Concept
1. Attacker registers/installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook subscribed by the app (e.g. `orders/create`) and captures the exact raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — this HMAC is valid because it was computed by Shopify using the app's shared `api_secret_key` over that raw body.
3. Attacker sends a new POST request to the app's webhook endpoint with:
   - the same raw body,
   - the same `X-Shopify-Hmac-Sha256` value,
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (an arbitrary/victim domain the attacker does not control).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` (`to_signable_string`) — this matches, so validation succeeds.
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, and the host application processes the event as if it legitimately originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
