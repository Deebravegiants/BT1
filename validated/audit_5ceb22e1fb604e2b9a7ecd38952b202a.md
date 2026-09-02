### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that downstream handlers use to attribute the event to a specific merchant are taken directly from unauthenticated HTTP headers that are never included in the signed material. This breaks the identity binding: `HMAC-verified bytes == raw_body` while `shop used for tenant attribution == unauthenticated header value`, which should instead be `shop used for tenant attribution == shop bound inside the verified payload`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are not part of the signed data: [2](#0-1) 

`Registry.process` validates only this body HMAC and then dispatches to the handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e. the raw body, using the app's single `api_secret_key`: [4](#0-3) 

Because the `api_secret_key` is the app's global client secret — shared across every shop that installs the app — a user who has legitimately installed the app on their own store receives genuinely-signed webhooks (valid `hmac-sha256` header over some `raw_body`). That attacker can replay the exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed because the shop header is never part of the signed content, and `Registry.process` will invoke the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` attributing the forged event to the victim shop. [5](#0-4) 

This is the same bug class as the report: an identity/authorization-relevant field (`shop`, the tenant key) is not covered by the same authentication mechanism (`HMAC`) that gates acceptance of the request, so it can be substituted independently of the authenticated payload — exactly analogous to using an unauthenticated salt component to derive a security-relevant identity binding.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` from `Registry.process` to select which merchant's session/data to update (as documented in `docs/usage/webhooks.md`) is exposed to cross-tenant webhook injection: a malicious but otherwise unprivileged app user can cause events (e.g., `app/uninstalled`, `orders/create`, `customers/redact`) to be falsely attributed to a different shop that also uses the app, potentially triggering data deletion, unauthorized data mutation, or GDPR-redaction actions against a shop the attacker does not control. This is a cross-tenant integrity/authorization violation.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free-tier) installer of the target app — a low bar, satisfying the "unprivileged internet user" threat model — plus the ability to POST to the app's public webhook endpoint with custom headers, which is inherent to how webhook endpoints work. No access to the app's `api_secret_key` or to the victim's credentials is needed.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the authenticated material, e.g., by requiring the caller to pass the expected shop domain into `Registry.process`/`HmacValidator.validate` and rejecting the request unless it matches a shop the gem can independently verify (or, at minimum, document loudly that `request.shop` is unauthenticated and must never be used as a tenant key without additional binding). Where possible, incorporate the `x-shopify-shop-domain` header into the signature verification input so it cannot be altered independently of the signed HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, obtaining a genuinely Shopify-signed webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid against the app's shared `api_secret_key`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally alters `x-shopify-topic`, since it too is unsigned).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and matches `H` — validation succeeds. [6](#0-5) 
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: parsed_body, ...)`, causing the host application to act on victim data using attacker-supplied content.

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
