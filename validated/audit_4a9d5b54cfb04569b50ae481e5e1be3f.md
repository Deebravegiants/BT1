### Title
Webhook shop-domain (and topic/webhook_id) attribution is not covered by the HMAC signature, allowing tenant-spoofed webhook injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before dispatching webhook data to the app's handler [1](#0-0) . In practice, `Utils::HmacValidator.validate` only proves that the **raw body** was signed with the app's `client_secret`; the `shop`, `topic`, `webhook_id`, and `api_version` values, which are read straight from HTTP headers, are never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled unauthenticated from headers [3](#0-2) . `Registry.process` validates only this body-derived HMAC and then trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

This breaks the identity-binding equality that the module name (`VerifiableQuery`) and the docs imply: `hmac_covers(shop) == shop_used_for_tenant_attribution`. In fact `hmac_covers(shop) = false`.

Because the app's `client_secret` is required to forge a valid HMAC over an arbitrary body, an unprivileged internet user cannot fabricate webhook bodies out of thin air. However, any user who can install the app on their own shop can obtain arbitrarily many legitimate `(body, hmac)` pairs signed by the real Shopify secret (e.g., by triggering their own `orders/create`, `app/uninstalled`, etc.). Since the webhook HTTP endpoint is a plain public POST endpoint under the host application's control, and this gem's `Request` constructor accepts any `headers` hash supplied by the caller, an attacker who replays that captured `(raw_body, hmac)` pair while substituting an arbitrary `shopify-shop-domain` header value produces a `Request` object that still passes `HmacValidator.validate` — the swapped `shop` header is never re-verified.

### Impact Explanation
This is a cross-tenant confusion primitive at the library boundary: the one field that `Registry.process` hands to every app's `WebhookHandler` for tenant routing (`data.shop`) is not covered by the same cryptographic check that authenticates the payload. Any handler that uses `data.shop` to decide which merchant's session/access token/record to act on (exactly what the gem's own documentation recommends, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to attribute attacker-supplied (from their own shop) webhook data to an arbitrary victim shop domain, or vice versa, without ever needing the app's `client_secret`. This matches the Critical "cross-tenant access" category since it defeats the tenant-isolation guarantee the HMAC check is supposed to provide.

### Likelihood Explanation
Requires only that the attacker can install the target app on a shop they control (a normal, low-privilege action) to obtain a validly-signed `(body, hmac)` pair, and that they can send a normal HTTP POST to the app's public webhook endpoint with a custom `shopify-shop-domain` header — both are within reach of an unprivileged internet user and require no leaked secrets, TLS interception, or social engineering.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` values in the HMAC-signed material (or otherwise cryptographically bind them to the body), or require `Registry.process` to independently confirm that `request.shop` corresponds to a shop with an actively registered webhook subscription for that `webhook_id`/topic before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers for `orders/create`.
2. Attacker creates an order in their own store; Shopify sends a legitimate webhook to the app's public endpoint:
   - headers: `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC over raw_body>`
   - body: attacker-chosen order JSON.
3. Attacker captures `(raw_body, hmac)` and resends it to the same public endpoint, replacing only the header `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, and `Utils::HmacValidator.validate` returns `true` because it only recomputes the HMAC over `raw_body` [5](#0-4) .
5. `Registry.process` calls the app handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker-controlled data>, ...)` [6](#0-5) , so the app processes attacker-controlled data under the victim shop's tenant context.

### Citations

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

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
