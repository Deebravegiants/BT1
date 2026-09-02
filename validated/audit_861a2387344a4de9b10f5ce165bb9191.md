This is a valid analog to the H04 bug class: the webhook HMAC covers only the raw request body (bytes verified), while the `shop` (tenant identity) and `topic` used to dispatch the webhook are taken from unauthenticated HTTP headers (bytes parsed but not covered by the signature).

### Title
Webhook shop-domain and topic used for tenant dispatch are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` bind the HMAC verification to the raw request body only. The `shop` and `topic` values that `Registry.process` uses to route the payload to a merchant-specific handler are read from HTTP headers, which are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively, and `Request#hmac` reads the signature from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header [1](#0-0) . `Registry.process` validates only this body/HMAC pair via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` and `request.topic` — both read straight from headers via `shopify_header` — to select the handler and construct `WebhookMetadata` [2](#0-1) [3](#0-2) .

This breaks the intended equality: `shop_authenticated_by_hmac == shop_used_for_tenant_dispatch`. The HMAC binding is `HMAC(secret, raw_body) == signature_header`, which says nothing about the `shopify-shop-domain` or `shopify-topic` headers. Because `OpenSSL::HMAC` in `HmacValidator.compute_signature` signs only `verifiable_query.to_signable_string` [4](#0-3) , and for `Request` that string is just the body, an attacker who can produce (or replay/relay) a validly-HMAC'd body for topic A can pair it with an arbitrary `shopify-shop-domain` header to get it dispatched as if it belonged to a different merchant/tenant, or pair a body meant for one topic with a different `shopify-topic` header to invoke a different handler with attacker-controlled headers/body combination.

This mirrors the reported bug class exactly: a value used to make a security-relevant decision (`collateral`/here, tenant identity `shop`) diverges from the value actually protected by the cryptographic check (`collateralRequired`/here, the signed `raw_body`), because the code assumes the two quantities are bound together when they are not.

### Impact Explanation
`shop` is the tenant-identifying field passed into `WebhookMetadata` and handed to the app's handler code [2](#0-1) . Any host application that trusts `data.shop` from `WebhookMetadata` as an authenticated tenant identifier (a very common and expected pattern, since the gem exposes it as the trusted shop for the callback) can be made to process a cross-tenant payload if a network position exists to swap headers on an otherwise-valid signed body (e.g., a shared/misconfigured ingress, proxy, or replay from a party that captured one merchant's webhook and can alter transport headers before it reaches this gem, since only the body is authenticated). This is a tenant/identity-binding gap rather than a full body forgery, so the severity is bounded by what an attacker can control at the network/header level, but it is a cross-tenant boundary crossing of the kind called out as Critical impact by the rules.

### Likelihood Explanation
Exploitability requires a position that can influence headers independent of the signed body (e.g., a shared webhook endpoint behind a proxy/load balancer that does not itself bind headers to body, or any relay that forwards a captured, validly-signed body with modified headers). This is a realistic deployment condition for HTTP webhook delivery style but not remotely as trivially reachable as a pure unauthenticated network attacker without any such intermediary; likelihood is moderate and depends on deployment topology.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` headers into the material that is HMAC-verified (or otherwise cryptographically bind them to the body), e.g. by including a canonicalized representation of these headers in `to_signable_string`, or by validating that the decoded body itself contains/matches the shop and topic claimed in the headers before dispatch.

### Proof of Concept
1. Attacker/network intermediary captures a legitimately Shopify-signed webhook body `B` (with valid `hmac` computed over `B`) for shop `victim-shop.myshopify.com`, topic `orders/create`.
2. Intermediary resends the same body `B` (and hence same valid HMAC) to the app's webhook endpoint, but rewrites the `shopify-shop-domain` header to `attacker-shop.myshopify.com` and/or `shopify-topic` to a different registered topic.
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B)` [5](#0-4) .
4. `Registry.process` dispatches the handler registered for the rewritten topic and passes `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [2](#0-1) , with `shop`/`topic` now attacker-controlled despite the "valid" HMAC.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
