Confirmed: the webhook signature covers only the raw body, not the `shop`, `topic`, or `webhook-id` headers.### Title
Webhook shop/topic identity not covered by HMAC signature enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and attribute the webhook to a specific merchant are taken directly from unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body signature and then trusts these unsigned header values to dispatch the event, breaking the intended binding of "authenticated bytes" (the body) to "the shop the event is acted on for" (the header).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches the handler using the unsigned `request.topic`, `request.shop`, and `request.webhook_id`: [4](#0-3) 

This is the same bug class as the escrow report: a value (`arbitratorFee` / here, `shop`+`topic`) is used to drive a privileged action (release funds / here, route+process tenant data) without being covered by the binding mechanism (multi-party agreement / here, the HMAC signature) that is supposed to authorize it. The equality that should hold — `shop_bound_by_signature == shop_acted_on` — does not: the signature binds only to `raw_body`, not to `shop`.

### Impact Explanation
Because the endpoint that receives webhooks is a normal public HTTP endpoint on the host app (reachable by any unprivileged internet user, not just Shopify's servers), anyone who can obtain one valid `(body, hmac)` pair — for example a merchant who installs the app on their own shop and simply captures a webhook Shopify sent them — can replay that exact body+signature to the same endpoint while forging the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers to claim the event belongs to a different shop/tenant or topic. `HmacValidator.validate` will still pass because it never inspects those headers, and `Registry.process` will hand the forged `shop`/`topic`/`webhook_id` straight to the app's `WebhookHandler`. Depending on how the host app keys its per-tenant data off `data.shop`, this enables cross-tenant data injection/corruption (e.g., writing another shop's uninstall/redact/data-request event, or an arbitrary GDPR-mandatory topic, under a spoofed shop identity) without ever possessing the app's `api_secret_key`.

### Likelihood Explanation
Exploitation requires only one legitimately captured `(body, hmac)` pair from any single tenant (trivial for anyone who can install/uninstall the app themselves) plus the ability to POST arbitrary headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed, which is why this is a realistic, unprivileged-attacker-reachable analog rather than a purely theoretical one.

### Recommendation
Bind the identity fields into the signed material instead of trusting unsigned headers: include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the HMAC-signed content, or have `Registry.process` independently verify that the `shop` header corresponds to a shop the app has an active session/webhook registration for before dispatching to the handler. At minimum, document that consuming applications must not treat `WebhookMetadata#shop` as authenticated by the HMAC and must independently validate it against known/installed shops (e.g., via `Utils::ShopValidator`) before using it as a tenant key.

### Proof of Concept
1. App installs webhook handling using `ShopifyAPI::Webhooks::Registry.add_registration` for topic `T1` on shop `shop-a.myshopify.com`.
2. Attacker (a real merchant on `shop-a.myshopify.com`) receives a genuine webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker replays the same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop) and/or a different `x-shopify-topic`.
4. `Utils::HmacValidator.validate` returns `true` because it only checks `B` against `H`, ignoring the shop/topic headers (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "<forged topic>", shop: "shop-b.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host app to process a spoofed cross-tenant event as if it legitimately came from `shop-b.myshopify.com`.

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
