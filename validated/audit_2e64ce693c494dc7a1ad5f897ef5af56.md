This confirms the vulnerability. The gem's own documentation instructs developers to trust `data.shop` as the tenant identifier — line 26 of `docs/usage/webhooks.md` shows the canonical usage pattern `perform_later(topic: data.topic, shop_domain: data.shop, ...)` — while `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` only cover the raw body, never the shop header.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header as the tenant identity handed to the app's handler. Because the signing secret (`Context.api_secret_key`, the app's `client_secret`) is identical for every shop that installed the app, a valid `(raw_body, hmac)` pair is not bound to any particular shop, allowing the `shop` field to be swapped freely while the HMAC still validates.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 
`hmac` is read from the `hmac-sha256` header and `to_signable_string` returns only `@raw_body`. The `shop` accessor is a separate, unrelated header read: [2](#0-1) 

`Registry.process` validates the request purely against `to_signable_string` (the body), then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it to the `hmac` header — the `shop-domain` header is never part of the signed material: [4](#0-3) 

Because `api_secret_key` is the app's single `client_secret` shared across *all* installing shops (not a per-shop secret), any `(body, hmac)` pair that is valid for shop A is also cryptographically valid when replayed with the `shop-domain` header changed to shop B — the signature check in `HmacValidator.validate` has no way to detect the substitution. The equality the design implicitly assumes is:
`shop that produced a valid HMAC == shop identity delivered to the handler`
but the actual guarantee provided is only:
`body integrity verified with app secret == valid`, with `shop` carried out-of-band and unauthenticated.

The gem's own documentation instructs consumers to key their business logic (e.g., persistence, job dispatch) directly off `data.shop`: [5](#0-4) 
so this un-bound field is acted upon as the tenant identity exactly as the rules describe ("a field acted on but not covered by the HMAC").

### Impact Explanation
If an attacker can obtain any one valid `(raw_body, hmac)` pair for the app (e.g., from a shop they themselves control and install the app on, or from webhook content whose body doesn't vary by shop), they can replay that payload to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain`/`shopify-shop-domain` header value. `Registry.process` will validate the HMAC successfully (it never inspected the shop header) and will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen shop. Any host application that uses `data.shop` to look up sessions, write records, or trigger per-tenant side effects (as the gem's own docs recommend) will act on forged data attributed to a victim tenant — a cross-tenant data integrity/confusion issue.

### Likelihood Explanation
Any developer building a multi-tenant Shopify app installs the same app (and thus the same `client_secret`) across many merchant shops, so an attacker with a legitimate installation of the target app on their own shop can trivially generate a valid `(body, hmac)` pair and then swap the shop header before forwarding it to the same app's public webhook endpoint. No access token, TLS interception, or privileged credentials are required — only installing the app once, which is normal, unprivileged behavior.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise independently authenticate it: for example, verify the webhook's shop against a per-shop expectation known from the registered session before dispatching to the handler, or include the `shop-domain` header in the signable string used for HMAC comparison (mirroring how `AuthQuery#to_signable_string` binds `shop` into its own HMAC in `lib/shopify_api/auth/oauth/auth_query.rb`). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated and must not be trusted for tenant-sensitive decisions without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, obtaining a legitimate webhook delivery with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint:
```
POST /callback/orders/create
shopify-topic: orders/create
shopify-hmac-sha256: H
shopify-shop-domain: victim-shop.myshopify.com
Body: B
```
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and finds it equal to `H` — validation passes because `shop` was never part of the signed content [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , causing the host application to process attacker-controlled data as if it originated from `victim-shop`.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
