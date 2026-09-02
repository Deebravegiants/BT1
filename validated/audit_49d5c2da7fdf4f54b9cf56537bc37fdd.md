### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and signs only the raw HTTP body, while the `shop` (and `topic`, `api-version`, `webhook-id`) values are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then trusts the header-derived `shop` value to build `WebhookMetadata`, which is what host applications use to route webhook data to the correct tenant.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body` — none of the HTTP headers are included in the signed material: [2](#0-1) 

Yet `shop`, `topic`, `api_version`, and `webhook_id` are all sourced from headers (`shopify-shop-domain` / `x-shopify-shop-domain`, etc.), which are attacker-controllable when a request is not routed through Shopify's own delivery infrastructure (e.g., in any test harness, proxy, or bridged delivery path an app operator wires up), and, more importantly, whenever an attacker is able to replay a *body+hmac pair they legitimately obtained for their own shop* against the app's webhook endpoint with a modified `shop-domain` header: [3](#0-2) 

`Registry.process` only checks the HMAC validity and then immediately trusts `request.shop` as the tenant identity for the handler: [4](#0-3) 

This is precisely the "field acted on but not covered by the HMAC" pattern: the binding that should hold is `hmac == HMAC(secret, shop ‖ topic ‖ body)`, but the gem only enforces `hmac == HMAC(secret, body)`, leaving `shop` (the tenant identity) unauthenticated. Because all shops that install the same app share the same `client_secret`, an attacker who controls their own shop can generate a validly-signed webhook body (any topic they can trigger, e.g. `orders/create` with attacker-controlled content) and then present it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, or an arbitrary attacker-controlled domain. The HMAC still validates because it never covered the header.

### Impact Explanation
This breaks the tenant boundary the app relies on: `WebhookMetadata.shop` is used by the host application to look up sessions/data for the correct merchant. An attacker forging the `shop` value can inject data attributed to a shop they do not own, corrupting per-tenant records or triggering shop-scoped side effects (e.g., customer/order redaction workflows, GDPR handlers) for a shop the attacker doesn't control — a cross-tenant integrity/authentication issue for the identity binding this gem is trusted to enforce.

### Likelihood Explanation
Exploitability depends on the attacker being able to reach the app's webhook endpoint with a crafted body/HMAC/header combination — trivial if the app's webhook route is reachable over the internet and not itself binding the `shop-domain` header to the source IP/URL path the way Shopify's real delivery would. Since the gem's own `HmacValidator`/`Request` abstraction provides no defense against this by design, any app that relies solely on `ShopifyAPI::Webhooks::Registry.process`'s HMAC check for authenticity is exposed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material (`to_signable_string`) for webhook requests, or otherwise cryptographically bind them to the HMAC, so that the identity of the shop cannot be altered independently of the signed payload.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body and the resulting `X-Shopify-Hmac-Sha256` header — both are legitimately signed with the app's shared `client_secret`.
2. Attacker replays this exact body and HMAC header to the app's public webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC — the forged `shop-domain` header is never part of the signed input. [5](#0-4) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually originated from the attacker's own shop, causing the app to process attacker-controlled data under the victim's tenant identity.

### Citations

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
