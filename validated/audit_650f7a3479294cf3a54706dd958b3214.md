### Title
Webhook `shop-domain` Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its `hmac` and `to_signable_string` from the raw request body only, while the `shop` value used downstream for tenant identification is read from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity without any cryptographic binding between the two. Because the webhook signing secret (`Context.api_secret_key` / `old_api_secret_key`) is the same for every shop that has the app installed, an attacker who controls (or has installed the app on) any shop can capture a validly-signed webhook and replay it against the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, producing a request that passes HMAC validation yet claims to originate from the victim tenant.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body (`@raw_body`), and `hmac` is derived from the `hmac-sha256` header: [2](#0-1) 

Crucially, `shop` (line 20-23) is read straight from the `shop-domain` header and is **not part of the signed material** — nothing in `to_signable_string` includes it: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed into the handler, with no secondary binding check: [4](#0-3) 

This is the exact identity-binding gap described in the rules: *"a field acted on but not covered by the HMAC"*. The equality that should hold — `shop-that-was-authenticated == shop-that-is-acted-on` — is broken: HMAC authenticates *"this exact body was produced with the app's secret"*, but the code acts on a header-derived shop that the signature says nothing about.

Because the webhook signing secret is the app's single `client_secret`/`api_secret_key`, shared across every shop that installs the app, any attacker who installs the app on an attacker-controlled shop (or otherwise observes one legitimately-signed webhook delivery) obtains a `(raw_body, hmac)` pair that is valid for the app's secret. The attacker can then send this exact body+hmac to the app's public webhook receiving endpoint while substituting the `shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` dispatches to the handler with `shop: <victim-shop>`.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` (or `request.shop`) as the tenant key to look up sessions, write data, or route business logic — which is exactly the pattern this gem's own webhook docs/tests encourage — can be made to process attacker-supplied webhook payloads as if they came from a victim shop. This is a cross-tenant access primitive: the attacker controls both the payload and the claimed tenant, while the gem's only verification (the HMAC) is silent about which tenant the payload belongs to. This satisfies the Critical severity bar ("cross-tenant access").

### Likelihood Explanation
The attacker only needs the ability to install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant/developer) to obtain a validly-HMAC-signed webhook body, and the ability to send an HTTP request to the app's public webhook endpoint with custom headers. No access token, `client_secret`, or privileged credentials are required — the shared signing secret is exactly what makes the replay-with-swapped-header trick work across tenants.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed material, or otherwise cryptographically bind `request.shop` to the verified payload before it is used as a tenant key — e.g., verify that the `shop-domain` header matches a shop portion embedded in the signed body/topic, or require callers to cross-check `request.shop` against an independently established session/shop record rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers/receives any webhook (e.g. `orders/create`). They capture the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header value Shopify sent — this HMAC is valid because it's signed with the app's single, shop-independent `api_secret_key`.
2. Attacker crafts a new HTTP request to the app's webhook endpoint using the captured `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but sets:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Topic: orders/create
   ```
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`:
   - `Utils::HmacValidator.validate(request)` succeeds because it only recomputes HMAC over `@raw_body`, matching the header the attacker kept unchanged (`lib/shopify_api/webhooks/request.rb:10-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
   - `Registry.process` then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using `request.shop`, which returns `"victim-shop.myshopify.com"` from the attacker-controlled header (`lib/shopify_api/webhooks/registry.rb:188-200`).
4. The host app's webhook handler processes the attacker's data believing it originated from `victim-shop.myshopify.com`.

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
