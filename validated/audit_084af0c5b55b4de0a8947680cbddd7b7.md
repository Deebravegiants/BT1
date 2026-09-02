Based on my analysis, I found a valid analog vulnerability in the webhook processing path.

### Title
Webhook `shop` attribution is trusted without HMAC coverage, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw body, then attributes the webhook to whatever shop domain is present in the `X-Shopify-Shop-Domain` header — a value that is never included in the signed payload. Any actor who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` (e.g., by triggering a webhook on their own, legitimately installed store) can replay that exact body to the app's webhook endpoint while substituting a different shop domain header, and the HMAC check will still pass. This breaks the intended binding "shop attributed to webhook == shop that generated and was authorized to sign the webhook."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the HMAC signature: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes the HMAC purely over `to_signable_string` (the body) and compares against the `hmac` header — it never factors in `shop`, `topic`, or `webhook_id`: [3](#0-2) 

After this check passes, the unauthenticated `request.shop` value is forwarded directly into `WebhookMetadata`, which the host application's handler uses to attribute/route the webhook data to a specific tenant: [4](#0-3) [5](#0-4) 

Since Shopify computes the webhook HMAC using the app's single shared `client_secret` for *all* shops that install the app (not a per-shop secret), a merchant/attacker who has legitimately installed the app on their own store, Shop A, can trigger a webhook to get a `(raw_body, hmac)` pair that will validate successfully under the app's secret. They can then send that same body/hmac pair directly to the app's public webhook endpoint with the `shop-domain` header changed to a victim's shop, Shop B. `HmacValidator.validate` will accept it because the signature only covers the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` even though the payload/signature never came from Shop B.

The intended binding is `authenticated_signer == shop_attributed_in_metadata`; the actual code enforces only `hmac(body) == signature`, leaving `shop` completely uncoupled from the cryptographic check.

### Impact Explanation
This is a cross-tenant integrity/confusion vulnerability: an app's own handler code typically uses `data.shop` to key persistence, authorization, and business logic (as shown in the gem's own documentation example that uses `data.shop` to route work by `shop_domain`). An attacker-controlled shop can forge webhook payloads that the host app will process as belonging to any other shop of the attacker's choosing, since the shop domain is fully attacker-supplied and unauthenticated. Depending on how the host app trusts `data.shop`, this can lead to data being attributed to, or overwriting, the wrong tenant's records — a cross-tenant access/integrity issue.

### Likelihood Explanation
Exploitation requires only: (1) ability to install the target app on an attacker-controlled development/partner store (freely available to any developer), (2) triggering any webhook topic the app subscribes to in order to obtain one valid `(body, hmac)` pair, and (3) sending an HTTP POST to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. No access token, `client_secret`, or privileged credentials of the target shop are needed — only a normal, unprivileged Shopify Partner/developer account, which matches the "unprivileged internet user" threat model.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable content, or independently verify that the shop domain in the header corresponds to a shop with an active session/installation known to the app before trusting `request.shop` for tenant attribution in `Registry.process`. At minimum, document that `data.shop` from `WebhookMetadata` is not itself authenticated and must be cross-checked against the app's own installed-shop records before being used for tenant-scoped operations.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com` and register for a webhook topic (e.g. `orders/create`).
2. Trigger that event on `attacker.myshopify.com`; Shopify sends a webhook POST with a `raw_body` and `X-Shopify-Hmac-SHA256` computed with the app's shared `client_secret`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Capture this exact `raw_body` and `hmac` header value.
4. Send a new POST to the app's public webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-SHA256`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds ( [6](#0-5) ), then invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` ( [7](#0-6) ), despite the payload never having been generated by or authorized for `victim-shop.myshopify.com`.

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
