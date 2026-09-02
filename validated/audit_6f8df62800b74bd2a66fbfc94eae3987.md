### Title
Webhook `shop-domain`, `topic` and `webhook-id` fields are trusted for tenant routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
The webhook HMAC-verification path validates only the raw request body, not the identity headers that the registry uses to route and attribute the event. `ShopifyAPI::Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers: [2](#0-1) 
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. only the body, and compares it with the received `hmac` header: [3](#0-2) 
`Registry.process` gates handler dispatch on this body-only HMAC check and then forwards the *header-derived* `request.shop` into `WebhookMetadata`, which is handed to the app's handler as trusted tenant identity: [4](#0-3) 

This is the exact bug class described in the analog rules: a value the app acts on (`shop`) is not covered by the HMAC that is supposed to authenticate the request. Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly folds `shop` into the signed string, so `shop` is cryptographically bound to the signature there: [5](#0-4) 

The binding that should hold is: `hmac_valid(raw_body, secret) == true` should imply `shop header is authentic for this raw_body`. In this gem's webhook path, that implication does not hold — `hmac_valid` only proves the body was signed by *someone holding the app's shared `client_secret`* (the same secret is used for every shop that installs the app), it proves nothing about which shop the header claims to be from.

### Impact Explanation
Because the app's `client_secret` is shared across all merchants who install the app, any merchant who installs the app on their own store receives genuinely-signed `(raw_body, hmac)` pairs from Shopify. Since the shop-domain/topic/webhook-id headers are not part of the signed material, that same attacker can replay the identical `raw_body`+`hmac` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a victim shop's domain. `HmacValidator.validate` still returns `true` (it never inspects the header), so `Registry.process` will invoke the app's handler with `WebhookMetadata` attributing the (attacker-controlled) body to the victim shop. This is a cross-tenant data-integrity/authentication issue: an app built on this gem's webhook API cannot distinguish "this body was really sent by Shopify for shop X" from "this is a genuine signature for shop Y's data, replayed with shop X's header." Depending on how the app persists/updates tenant records from webhook data (a normal and encouraged usage per the gem's documented handler pattern), this enables injection of forged/cross-tenant order, product, or customer data attributed to a victim's shop.

### Likelihood Explanation
Exploitation requires only: (1) the attacker install the target app on their own (attacker-controlled) shop — a normal, unprivileged action any merchant can take — to obtain one legitimate `(raw_body, hmac)` pair, and (2) the ability to POST to the app's public webhook endpoint with custom headers, which is inherent to any HTTP endpoint exposed to receive webhooks. No access token, `api_secret_key`, or privileged access is required, satisfying the "unprivileged internet user" constraint. The main variable is how strictly a given `raw_body` structurally matches what the app expects for the target topic, but the identity-binding defect itself is unconditionally present.

### Recommendation
Bind the identity headers into the HMAC-signed material (or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the verified signature), e.g. by having `Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` alongside the raw body (mirroring what `AuthQuery#to_signable_string` already does for `shop`), or by requiring/validating that the `shop` header matches a shop the app has an active session/installation for before invoking the handler in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, becoming a legitimate (if unprivileged, non-victim-tenant) recipient of webhooks signed with the app's shared `client_secret`.
2. Shopify sends a webhook to the app's public callback URL with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this `(B, hmac)` pair and replays it directly to the app's webhook endpoint, but swaps the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. On the server, `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to the (still-valid) `hmac` header — validation succeeds because `to_signable_string` never included the shop header. [4](#0-3) 
5. The app's registered handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"`, even though the signed payload `B` actually originated from the attacker's own shop's events, achieving cross-tenant attribution of forged data.

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
