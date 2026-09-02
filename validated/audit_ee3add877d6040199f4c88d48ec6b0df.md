This confirms the finding is well grounded in documented, intended usage: the handler receives `data.shop` (from `WebhookMetadata`) as the identity used to determine "which shop's records to update"### Title
Webhook HMAC signature covers only the raw body, not the shop-identifying header, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `Utils::HmacValidator.validate` verifies the HMAC exclusively against that signable string [2](#0-1) . The `shop`, `topic`, and `webhook_id` values consumed by the app are read from HTTP headers that are never part of the signed payload [3](#0-2) . `Registry.process` trusts these header-derived values once the body HMAC passes, and hands them straight to the app's handler as the tenant identifier [4](#0-3) .

### Finding Description
The binding that should hold is: **shop authenticated by the cryptographic signature == shop the handler acts on**. In this gem that equality is broken because the HMAC is computed only over `@raw_body` [5](#0-4) , but `request.shop` (and `topic`/`webhook_id`) come from `x-shopify-shop-domain` / `shopify-shop-domain` headers that are parsed but never covered by the signable string [6](#0-5) .

Because the webhook secret used for HMAC (`Context.api_secret_key`) is the app's single client secret shared across every shop that installs the app (not per-tenant), any user of the app can obtain a legitimately-signed raw body: they install the app on their own shop, trigger a real event, and receive a webhook whose body-only HMAC is valid. They can then replay the exact same raw body to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop the attacker does not control. `HmacValidator.validate` will still pass because it only checks the (unchanged) body bytes against the secret [7](#0-6) , and `Registry.process` will dispatch the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain [8](#0-7) , [9](#0-8) .

This is the direct analog of the report's bug class: a field that is *acted upon* (the tenant/shop identity used to route and key state) is not the field that is *cryptographically verified* (only the body is). Just as the Connext report showed `msg.sender`/`msg.value` being trusted without being bound to a legitimate cross-chain intent, here the `shop` field the handler uses for cross-tenant state is trusted without being bound to the HMAC that "proves" the message's authenticity.

### Impact Explanation
This enables cross-tenant confusion/spoofing: an attacker with a legitimate but low-trust relationship to the app (any merchant who can install it and generate their own webhook traffic) can make the app believe an arbitrary event body originated from a different, victim shop. The gem's own documentation instructs handlers to key their side effects by `data.shop` (e.g. `shop_domain: data.shop`) exactly as shown in `docs/usage/webhooks.md`, meaning apps built per this library's documented contract will act on webhook payloads keyed to the wrong tenant. Depending on the handler logic, this can lead to cross-tenant data writes/reads keyed by the forged shop — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Moderate-to-high: it only requires an attacker to (a) install the app on a shop they control (a normal, unprivileged action available to anyone) to obtain a genuinely-signed body, and (b) send an HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header, since headers are not bound by the signature. No access token, `client_secret`, or privileged credential is required — only knowledge of the public webhook path, which the app must expose to receive real webhooks.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed payload verification, or otherwise cross-check the header-derived shop against an independent trust source. Concretely:
- Have `Request#to_signable_string` incorporate the shop-domain, topic, and webhook-id headers (not just the raw body) so a captured valid body/HMAC pair cannot be replayed with different header metadata, or
- Require callers of `Registry.process` to supply the expected shop (e.g., from the route parameter/session lookup) and assert it matches `request.shop` before dispatch, rejecting mismatches, and
- Document explicitly that `request.shop` from headers is unauthenticated until such a check is added, since apps currently key business logic on it per the maintained documentation.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook for `orders/create`.
2. Shopify sends a legitimately-signed webhook: raw body `B` with header `x-shopify-hmac-sha256` computed as `HMAC-SHA256(api_secret_key, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact request (`B` and its valid HMAC header).
4. Attacker resends the identical raw body `B` and identical HMAC header to the app's public webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (i.e., `B` only) — it matches, so validation passes [10](#0-9) .
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [11](#0-10) , causing the app to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

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
