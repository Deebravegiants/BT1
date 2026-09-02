### Title
Webhook `shop`/`topic` metadata is not covered by the HMAC signature, allowing cross-tenant metadata forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` only validates the HMAC over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values it hands to the host application's handler are taken from unauthenticated HTTP headers that are never part of the signed bytes. This breaks the binding: `HMAC_valid(body) == true` should imply `shop header == authenticated tenant`, but it does not.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Utils::HmacValidator.validate` verifies the HMAC solely against that string: [1](#0-0) [2](#0-1) 

`Registry.process` then trusts `request.topic` and `request.shop`, which are read straight out of HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`, etc.) with no cryptographic tie to the signed body, and passes them into the handler's `WebhookMetadata`: [3](#0-2) [4](#0-3) 

Because the HMAC only signs `@raw_body`, an unprivileged user who legitimately receives a genuine webhook delivery for their own store (a valid `(body, hmac)` pair, which is not secret information — it is delivered to any store owner who controls a webhook endpoint) can replay that same body/hmac pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` header. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will invoke the handler with attacker-chosen `shop`/`topic`/`webhook_id` metadata that host applications are expected to trust as authoritative for tenant identification (per the gem's documented usage in `docs/usage/webhooks.md`, where `WebhookMetadata#shop` is the field apps use to scope database writes/lookups to a merchant).

This is the same class of bug as the reported issue in `MyStaking.sol`: verification is performed against one thing (there, `unclaimedAmount`; here, the raw body) while the state actually acted upon (there, cumulative rewards; here, the `shop`/`topic` identity) is a distinct value not covered by that verification, letting an attacker desynchronize the two.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` from this gem to select which tenant's data to update (the documented and expected usage pattern), an attacker who owns one shop can forge webhook headers to make the payload appear to originate from a different shop, causing cross-tenant data confusion/corruption in the host application — while never needing the app's `client_secret` or any privileged credential themselves (they only need a legitimate webhook delivery for their own shop, which Shopify sends them by design).

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to have their own store subscribed to webhooks from the target app (trivial to obtain by installing the app) and requires the host application to trust `shop`/`topic` from `WebhookMetadata` without independently cross-checking against a known shop-to-secret or per-shop webhook allowlist — which is exactly the pattern this gem's own documentation encourages.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or independently bind them, e.g., by validating `shop` against the session/shop this specific installation expects) instead of signing only the raw body, so the verified bytes and the identity fields acted upon by the handler are the same authenticated unit.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a genuine webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `B`/`H` pair to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [2](#0-1) , and `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` [3](#0-2) , letting the attacker inject data or trigger side effects attributed to `victim-shop`.

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
