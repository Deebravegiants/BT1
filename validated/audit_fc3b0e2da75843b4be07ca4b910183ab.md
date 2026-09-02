### Title
Webhook shop/topic identity spoofing via HMAC that only covers the request body - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop`, `topic`, `api-version`, and `webhook-id` values that the gem extracts from HTTP headers and hands to the app's handler as the webhook's identity are never included in the signed bytes. Any actor who can obtain one valid `(body, hmac)` pair for the app — trivially available to anyone who installs the app on their own store and receives a legitimate webhook — can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, causing the handler to process attacker-controlled data as if it originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC only against `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` performs exactly one authentication check — the body HMAC — and then trusts the header-derived `shop`/`topic` fields to build the identity object passed to the host app's handler: [4](#0-3) 

This breaks the intended identity binding: `hmac_valid(body) == true` is treated by the gem as equivalent to `shop header == authentic tenant for this body`, but those are two independent, unrelated facts. Because the same app-wide `api_secret_key` signs webhooks for every shop that installs the app, an attacker who is a normal merchant (installs the app on their own, possibly free, development store) will receive real webhooks with a valid `(raw_body, hmac)` pair for topics the app has registered. The attacker can then POST that identical body and HMAC directly to the app's public webhook URL while changing only the `x-shopify-shop-domain` header (and, if a matching handler exists, the `x-shopify-topic` header) to point at a victim shop. `HmacValidator.validate` will pass because it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` — attributing attacker-controlled data to the victim shop.

### Impact Explanation
Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (which is the gem's documented/intended way to key tenant data — see `docs/usage/webhooks.md`), this allows an unprivileged attacker to inject or attribute data under a victim shop's identity: e.g., forging an `app/uninstalled` event for a victim shop to trigger deletion of that shop's stored access token/session in the host app, or injecting attacker-controlled order/customer payloads that the host app associates with the victim's tenant. This is a cross-tenant identity-binding break entirely within the gem's own webhook verification logic, meeting the "cross-tenant access" criterion.

### Likelihood Explanation
Requires no leaked secrets, tokens, or privileged access — only that the attacker be a normal user able to install the target app on any store (including a free development store) and observe one legitimate webhook delivery for a topic the app has registered, then replay it against the app's public webhook endpoint with a modified shop-domain header. This is fully reachable through the gem's documented public API (`Webhooks::Registry.process`) with no reliance on the host app doing anything unusual.

### Recommendation
Bind the shop, topic, and other identity headers into the signed material verified by `HmacValidator`, or otherwise cryptographically tie them to the verified body (e.g., include them in `to_signable_string`, or independently verify `shop` against the session/shop the webhook was registered for before dispatching to handlers). At minimum, document and enforce that host applications must not trust `WebhookMetadata#shop`/`#topic` without additional verification, since only the body is authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (any user can create a development/partner store).
2. The app registers webhooks (e.g., `orders/create`); Shopify delivers a legitimate webhook to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`.
3. Attacker captures the raw body and HMAC from this legitimate delivery (e.g., from their own server logs, since it was addressed to them).
4. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with the identical raw body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over the (unchanged) body and it matches — validation succeeds.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's body content, causing the host application to process attacker-supplied data as belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
