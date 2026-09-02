### Title
Webhook `shop`, `topic`, and `webhook-id` headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the HMAC-signed payload, so they are unauthenticated even after the HMAC check passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Webhooks::Request#hmac` decodes the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers with no relation to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards these unauthenticated header values straight to the app's handler as trusted metadata: [4](#0-3) 

The binding that is broken is: `hmac == HMAC(raw_body, secret)` is verified, but the app's tenant-identifying field, `shop == header("shop-domain")`, is never bound to that HMAC. Any request whose body+HMAC pair is valid (e.g., a genuine webhook the attacker legitimately received for their own, attacker-owned shop, since installing an app and receiving its own real webhooks requires no privilege beyond being an ordinary merchant/unprivileged internet actor relative to the app) can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (and `x-shopify-topic`/`webhook-id`) header rewritten to name a different, victim shop. `HmacValidator.validate` only checks the body signature and has no knowledge of, or binding to, the shop header, so the forged request passes validation: [5](#0-4) 

The handler then receives `WebhookMetadata` with `shop: request.shop` attributing attacker-controlled webhook content to an arbitrary shop domain of the attacker's choosing.

### Impact Explanation
This breaks the tenant-identity binding at the point where the gem hands data to the host application: the host app is told "this webhook is for `shop`" based on an unauthenticated header, while the actual cryptographic proof only covers the body. A host application that uses `data.shop` (as returned by this gem) to select which tenant's records to update, this enables cross-tenant data corruption/injection — an attacker-controlled payload becomes attributable to a shop the attacker does not own, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: any developer/merchant who has installed the app and receives even one legitimate webhook payload with a valid HMAC can reuse that (body, hmac) pair indefinitely and relabel it to any `shop-domain` string, since the gem provides no mechanism binding the header to the signed content, and the only "privilege" required is having installed the app once as any tenant.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed payload (mirroring the approach used for `Auth::Oauth::AuthQuery#to_signable_string`, which does canonicalize and sign all fields it trusts), or otherwise cryptographically bind the shop identity to the payload before exposing it to handler code, so the shop attribution cannot be altered independently of the signed body.

### Proof of Concept
1. Attacker installs the target app for their own shop `attacker.myshopify.com` and receives a real webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the identical `raw_body` (`B`) and `hmac` (`H`) to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` and succeeds because `B` and `H` are unchanged, per `lib/shopify_api/webhooks/registry.rb:188-190` and `lib/shopify_api/utils/hmac_validator.rb:12-22`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body, ...)`, per `lib/shopify_api/webhooks/registry.rb:198-199`, causing the host app to process attacker-controlled data under the victim shop's identity.

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
