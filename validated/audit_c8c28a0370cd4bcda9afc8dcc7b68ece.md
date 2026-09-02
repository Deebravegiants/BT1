This confirms the root-cause analog: the webhook HMAC only signs the raw request body, while the `shop-domain` (and `topic`, `webhook_id`, `api_version`) headers that the gem hands to the app's handler as trusted identity are never part of the signed material.

## Title
Webhook shop-domain identity is not bound by the HMAC signature, allowing shop impersonation via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `ShopifyAPI::Webhooks::Registry.process` validates that string with `Utils::HmacValidator.validate` before handing `request.shop` (taken straight from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) to the app's handler as the authoritative tenant identifier.

### Finding Description
`Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
only the raw body bytes are covered by the HMAC. The `shop`, `topic`, `webhook_id`, and `api_version` accessors all read directly from HTTP headers that are not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The documented handler contract explicitly tells integrators that `data.shop` is "The shop domain of the webhook," implying it is a verified value: [4](#0-3) 

The identity binding that should hold is: `HMAC-verified bytes == bytes used to derive shop identity`. Here that equality breaks — `HmacValidator.validate` verifies `raw_body` against the secret, but `request.shop` is read from a header that is never included in `to_signable_string`. An unprivileged internet user who controls any merchant's own store (a completely legitimate, unprivileged Shopify merchant/developer account) can capture a real, validly-signed webhook body ever delivered for their own shop (webhook bodies for a given topic/version are often identical or predictable, e.g. `{}`-shaped payloads, or replayable bodies from their own store events), then POST that exact raw body to the victim app's webhook endpoint with the `X-Shopify-Hmac-Sha256` header from their own genuine webhook (valid, since it only signs the body) but with the `X-Shopify-Shop-Domain` header changed to any other shop domain. `HmacValidator.validate` still passes because it only checks the body bytes, and the gem forwards `shop: <attacker-chosen domain>` to the handler as if Shopify had authenticated it.

### Impact Explanation
This is a cross-tenant identity confusion: an app relying on `shopify_api` for webhook shop identity (as instructed by the gem's own documentation) can be made to process a webhook body under an arbitrary victim shop's identity without ever authenticating as that shop. Depending on the webhook topic (e.g., `app/uninstalled`, `shop/update`, billing/subscription topics), this can drive cross-tenant data corruption, forged deprovisioning, or state changes attributed to a shop the attacker doesn't own — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only an unprivileged Shopify merchant/developer account (installable for free) to legitimately receive at least one genuine webhook with a signature computed only over the body, and a public webhook endpoint reachable at the app's configured callback URL — both are the gem's documented, default configuration. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the shop (and topic/webhook_id/api_version) into the signed material check, or explicitly re-derive/verify `request.shop` from a source cryptographically tied to the HMAC (e.g., require the app to cross-check the delivered shop domain against the shop associated with the webhook subscription id via the Admin API), and update `to_signable_string` guidance/documentation to make clear headers are unauthenticated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic, receiving a legitimate request with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker crafts a new POST to the app's webhook endpoint with the same raw body `B`, the same header `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(secret, B)` and compares to `H` — it matches because only `B` is signed.
4. `Registry.process` calls the app handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to act on behalf of `victim-shop.myshopify.com` using attacker-supplied body content, despite no Shopify-authenticated request for that shop ever occurring. [5](#0-4)

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
