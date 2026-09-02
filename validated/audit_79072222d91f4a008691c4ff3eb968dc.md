Now I have enough evidence to confirm the analog: the `AuthQuery` includes `shop` (and `host`, `code`, `state`, `timestamp`) in the HMAC-signed string [1](#0-0) , but the webhook `Request` computes its HMAC over only the raw body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers [2](#0-1) . The `shop` value pulled from the unauthenticated header is what gets forwarded to the app's webhook handler as the tenant identity.

### Title
Webhook `shop` (and topic/id) header used for tenant routing is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the HMAC-signable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers that are never included in the signature computation.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it against the `hmac` field [3](#0-2) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [4](#0-3) , and `shop`, `topic`, `webhook_id` are parsed from headers that are completely outside that signed string [5](#0-4) . `Registry.process` validates the HMAC of the request and then immediately trusts `request.shop` as the tenant identity dispatched to the app's handler: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [6](#0-5) . This breaks the identity binding `shop_covered_by_hmac == shop_acted_on`: the body's authenticity is proven, but the `shop-domain` header used to attribute the payload to a specific merchant is not. Any component sitting between Shopify and the app that can rewrite headers without altering the body (a misconfigured/shared reverse proxy, an app that fronts multiple hosts behind one signature-checking layer, or any test/relay harness that reuses a captured body) can cause a genuine, HMAC-valid webhook body to be attributed to a different `shop` than the one Shopify actually sent it for. This contrasts with `Auth::Oauth::AuthQuery`, where `shop` (along with `host`, `code`, `state`, `timestamp`) is explicitly part of the signed string [1](#0-0) , showing the gem's own convention is to bind identity-relevant fields into the signature — a convention not followed for webhook headers.

### Impact Explanation
If the `shop` attribution can be desynchronized from the signed body while the HMAC still validates, an app relying on `Registry.process`/`WebhookMetadata#shop` to select which merchant's data store or session to write into can be made to apply one merchant's genuine webhook payload under a different merchant's identity — a cross-tenant data integrity issue reachable purely by manipulating headers that sit outside the gem's own authenticity boundary.

### Likelihood Explanation
Exploitability depends on the deployment having a component that can alter headers independently of the body before it reaches this gem's `Webhooks::Request`/`Registry.process` (e.g., a shared HMAC-terminating proxy, a webhook relay/replay tool, or an app that aggregates webhooks for many shops behind one endpoint). This is a plausible, non-exotic operational pattern for multi-tenant Shopify apps, but it is not exploitable by an anonymous internet attacker sending a single unmodified request directly to Shopify's servers, since Shopify itself sets the headers consistently with the body it signs.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (and `api_version`) in the HMAC-signed content for webhook requests, or otherwise cryptographically bind these header values to the body so that `Utils::HmacValidator.validate` fails if any of them are altered independently of the raw body.

### Proof of Concept
1. Capture a legitimate Shopify webhook: raw body `B` with headers `X-Shopify-Hmac-Sha256: H` (valid for `B`) and `X-Shopify-Shop-Domain: shop-a.myshopify.com`.
2. On the relaying/proxying layer (outside Shopify, e.g., a shared ingress that fans out to per-tenant apps), forward the same body `B` and the same `H` header, but rewrite `X-Shopify-Shop-Domain` to `shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: rewritten_headers)` is constructed; `Utils::HmacValidator.validate` recomputes HMAC over `B` only, which still matches `H` [7](#0-6) .
4. `Registry.process` passes validation and calls the handler with `shop: "shop-b.myshopify.com"` even though the signed body actually belongs to `shop-a` [8](#0-7) .

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
