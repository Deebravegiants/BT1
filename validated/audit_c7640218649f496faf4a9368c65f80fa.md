### Title
Webhook `shop` (and topic/api_version/webhook_id) header values are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against that signable string (the body). The `shop` value handed to application webhook handlers is therefore never bound by the HMAC that "authenticates" the request.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` only — none of the Shopify headers (including `shopify-shop-domain`) are part of the signed material.

`HmacValidator.validate` computes/compares the HMAC purely over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (sourced from the `x-shopify-shop-domain` header) to build `WebhookMetadata` that is passed to the developer's handler: [4](#0-3) 

Because the app's `api_secret_key` is the same across all shops that install the app, any merchant who has installed the app can trigger genuine webhooks for their own store, capturing a request with a **valid HMAC** (computed over their own body). Since the header `x-shopify-shop-domain` is not part of the signed content, that attacker-controlled merchant can replay/relay the exact same body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and other headers such as `topic`/`webhook-id`) with an arbitrary victim shop's domain. `HmacValidator.validate` still succeeds (body unchanged), and `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the forged victim domain — an equality the library treats as trusted (`shop_authenticated == shop_used_by_handler`) that in reality does not hold (`shop_authenticated (by HMAC) == body_only`, while `shop_used_by_handler == unauthenticated_header`).

This is exactly the "field acted on but not covered by the HMAC" bug class: the `data` field in the external report was unbound from the enforced constraint (sequence processing); here the `shop` field routed to tenant-specific handling logic is unbound from the enforced HMAC check.

### Impact Explanation
Downstream application code (using this gem's documented `WebhookMetadata#shop`, per `docs/usage/webhooks.md` intent) typically uses `data.shop` to resolve which merchant/session a webhook payload belongs to (e.g., to look up the shop's session/access token or to write shop-scoped records). An attacker who is a legitimate, unprivileged installer of the app for their own store can forge the shop-domain attribution of a webhook that appears to have passed HMAC validation, causing the host app to process attacker-controlled data under a victim shop's tenant identity — a cross-tenant impact.

### Likelihood Explanation
The attacker only needs to be an ordinary (even free/trial) installer of the target app — no access to the app's `client_secret`, no compromised credentials, and no privileged account are required. Capturing one's own valid webhook request and replaying it with a modified `shop-domain` header is trivial once the webhook endpoint is internet-reachable (which it always is, by design).

### Recommendation
Bind the shop (and other trust-relevant headers such as topic, webhook-id) into the HMAC-verified material, or otherwise independently corroborate the shop identity (e.g., cross-check against a shop-scoped secret, or require callers to fetch/verify shop identity via a separate authenticated channel rather than trusting the raw header). At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is NOT covered by HMAC verification and must not be used as a tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":123}` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the identical body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which only checks the HMAC against `raw_body` — validation succeeds: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop == "victim.myshopify.com"`, and the app processes attacker-supplied body content as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
