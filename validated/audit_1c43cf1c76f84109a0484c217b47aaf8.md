This confirms the analog. `AuthQuery.to_signable_string` explicitly includes `shop` (and `host`) as part of the signed payload, binding the shop identity to the HMAC. In contrast, `Webhooks::Request.to_signable_string` (returns only `@raw_body`) does not include the `shop` header at all, so `request.shop` is never covered by the HMAC computed in `Utils::HmacValidator.validate`.

### Title
Webhook `shop` identity is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, but the `shop` field that is passed to the app's webhook handler — and used to attribute the event to a tenant — is taken from an HTTP header that is never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only that `Utils::HmacValidator.validate(request)` passes (i.e., that the body's HMAC matches, using the app's shared `api_secret_key`), then immediately builds `WebhookMetadata` using `request.shop`, the unauthenticated header value, and hands it to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the HMAC purely over `verifiable_query.to_signable_string` (i.e., the body for webhooks): [4](#0-3) 

This is asymmetric with how the gem handles the OAuth callback: `Auth::Oauth::AuthQuery#to_signable_string` deliberately includes `shop` (and `host`) in the signed string, so the shop identity *is* bound to that HMAC: [5](#0-4) 

The webhook path breaks the equality that should hold: `shop-domain header == shop bound by HMAC signature`. Because the `api_secret_key`/`client_secret` used to HMAC-sign webhooks is shared by all shops using the same app (Shopify signs every webhook for every install of that app with the same app secret, not a per-shop secret), an attacker who is a legitimate merchant/install of the target app (an unprivileged internet user with respect to any other tenant) can obtain a validly-signed webhook payload for their own shop (e.g. by triggering `orders/create` on their own store) and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to point at a victim shop that also uses the app. The HMAC check still passes because it only covers the body, and the handler receives `WebhookMetadata` claiming it originates from the victim shop.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem, following the documented `Registry.process` pattern, will invoke the app's webhook handler believing the event came from a different merchant's shop than the one that actually sent it. Depending on how the host application keys data lookups off `WebhookMetadata#shop` (which is the sanctioned, documented field for this purpose), this can lead to cross-tenant data corruption/access — writing/deleting data under the wrong shop's session/record, or bypassing shop-scoped authorization checks that trust the field. This qualifies as Critical (cross-tenant access) per the scoring criteria, since it does not require the access token, `api_secret_key`, or any privileged credential — only being a customer of the same app.

### Likelihood Explanation
Requires no secrets: an attacker only needs to be an app install owner (any merchant can install a public app) capable of sending an arbitrary HTTP request with custom headers to the app's public webhook endpoint, and to have received a real webhook for their own shop to replay with a substituted domain header. This is realistic and requires no interaction with Shopify's servers beyond normal use.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the value cryptographically bound to a per-request check, or otherwise cross-check `request.shop` against externally known/trusted state before trusting it (e.g., verify the shop is a session the app expects, or document to consumers that `shop` from `Webhooks::Request` must not be trusted for authorization without an independent shop existence check). At minimum, the library should not offer `WebhookMetadata#shop` as if it were verified, since `HmacValidator.validate` never covers it.

### Proof of Concept
1. Attacker (App user A, shop `attacker.myshopify.com`) installs the vulnerable app and triggers a legitimate webhook (e.g., updates an order) so Shopify sends a validly HMAC-signed `orders/updated` payload to the app's webhook endpoint, with header `X-Shopify-Shop-Domain: attacker.myshopify.com` and `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`.
2. Attacker intercepts/replays this exact request to the same endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (a real shop that also installed the app), leaving body and HMAC header untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body`, i.e., `lib/shopify_api/utils/hmac_validator.rb:26-31` — validation succeeds because the body wasn't modified.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, `lib/shopify_api/webhooks/registry.rb:198-199`, even though `victim.myshopify.com` never sent this event, letting the attacker inject/replay forged data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
