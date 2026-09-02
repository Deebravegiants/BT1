Confirmed: `WebhookMetadata` (`lib/shopify_api/webhooks/webhook_handler.rb:6-12`) carries `shop`, `topic`, `webhook_id`, and `api_version` straight from unauthenticated HTTP headers, and `VerifiableQuery#to_signable_string` (`lib/shopify_api/utils/verifiable_query.rb:11-15`) for `Request` only covers `@raw_body`. This confirms the identity-binding gap.

### Title
Webhook shop/topic/id identity fields are not covered by HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking the HMAC of the raw request body. All identity-carrying fields that the handler actually trusts and acts on — `shop`, `topic`, `webhook_id`, `api_version` — are read directly from HTTP headers and are never included in the signed material, so they can be freely altered without invalidating the signature.

### Finding Description
`Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) calls `verifiable_query.to_signable_string` and compares it against the received HMAC using the app's shared `api_secret_key`. For webhook requests, `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled unauthenticated from headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:20-33, 67-70`).

`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates only the body HMAC, then builds `WebhookMetadata` directly from these unauthenticated header values and hands it to the app's handler:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
The binding the code implicitly claims is: *`shop` (and `topic`/`webhook_id`) header value == the tenant that produced the HMAC-signed body*. In reality only the raw body bytes are bound to the signature; the header-derived tenant identity is not. Because `api_secret_key` is shared by the app across every merchant that installs it, any merchant who can trigger a webhook for their own shop obtains a body+HMAC pair that is valid for that secret — and can then replay that exact body with a forged `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header pointing at a different, victim shop. `Registry.process` will accept it, since HMAC validation never inspects the headers.

This is the analog of the reported bug class: an identity/state field (`shop`) is acted upon by downstream logic without being covered by the authenticating check (HMAC), exactly like `$.numExchangableNFT`/fee being consumed without being kept consistent with the authenticated mutation.

### Impact Explanation
Webhook handlers commonly perform tenant-scoped, security-relevant actions keyed off `data.shop` — e.g., deleting shop data on `app/uninstalled`, deactivating billing, or updating per-shop feature flags. An attacker who legitimately controls one shop (installs the app themselves, a normal unprivileged action) can forge the `shop` header to point at an arbitrary victim shop while replaying a validly-HMAC'd body from their own tenant. This crosses the tenant boundary purely by exploiting the gem's own authentication logic (HMAC validates bytes it does not fully bind), qualifying as Critical - cross-tenant access.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged onboarding action) and send an HTTP request with attacker-chosen headers to the app's public webhook endpoint — which is inherently internet-reachable since Shopify itself delivers webhooks to it. No leaked secrets, tokens, or privileged access are needed; the gem's own `Request`/`Registry` code path is what fails to bind headers to the signature.

### Recommendation
Include the security-relevant header fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material (or otherwise cryptographically bind them to the body, e.g. via a canonical string that concatenates headers + body before computing/verifying the signature), so that altering any of these fields invalidates the signature. At minimum, cross-check `request.shop` against an expected/known shop for the active session or app installation before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged flow) and triggers a webhook-eligible event (e.g., `orders/create`), causing Shopify to POST a body `B` with a valid `X-Shopify-Hmac-Sha256` header `H` (computed with the app's shared `api_secret_key`) to the app's webhook endpoint.
2. Attacker intercepts/replays this exact request but rewrites the header `shopify-shop-domain` (and optionally `shopify-topic`, `shopify-webhook-id`) to reference `victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B) == H`, which is unchanged — headers were never part of the signed string.
5. `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...))` is invoked, causing the app to perform tenant-scoped actions against the victim shop using attacker-controlled data. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
