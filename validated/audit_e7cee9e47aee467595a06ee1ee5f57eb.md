### Title
Webhook shop/topic identity spoofing via unsigned headers - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC computed by `HmacValidator.validate` covers exclusively the JSON payload bytes. The `shop-domain`, `topic`, `webhook-id` and `api-version` values are read straight from HTTP headers and are never included in the signed content, yet `Registry.process` trusts them to route and label the webhook to the app's handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which only exposes `@raw_body`. `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`HmacValidator.validate` verifies the signature strictly against `to_signable_string` (i.e., the body only): [3](#0-2) 

`Registry.process` accepts the request as authentic once this body-only HMAC passes, then forwards the *unsigned* `request.shop` and `request.topic` values to the app's handler for tenant-scoped processing: [4](#0-3) 

The identity binding that should hold is: `shop/topic authenticated == shop/topic acted on`. Because the app-level `api_secret_key` used to compute the HMAC is the same across every shop installed on that app (it is not shop-specific), an unprivileged attacker who controls **any** single shop that has this app installed can:
1. Trigger a legitimate webhook delivery from Shopify for a topic/body they fully control (e.g. by creating an order in their own store to fire `orders/create`), obtaining a validly-signed body+HMAC pair signed with the app's shared secret.
2. Replay that exact body and HMAC to the app's public webhook endpoint, but with the `shopify-shop-domain` (and optionally `shopify-topic`) header rewritten to name a different, victim shop.

`HmacValidator.validate` still returns `true` because the signed bytes (body) are unchanged, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop, even though it was never authenticated as such — the header value was never covered by the HMAC.

### Impact Explanation
This breaks the binding `shop authenticated == shop acted on`, letting an attacker cause the host application to process attacker-controlled body content under a spoofed victim shop identity. Since apps commonly use `webhook.shop` to select which tenant's session/access token to load or which tenant's records to mutate, this is a cross-tenant confusion vector rooted entirely in this gem's `Request`/`HmacValidator`/`Registry` implementation, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any developer/merchant who can install the target app on a shop they control (a normal, unprivileged onboarding step for public or even custom apps) can trigger real webhooks with attacker-chosen body content and then simply resend the captured request with one header value swapped — no access to `api_secret_key`, access tokens, or TLS interception required.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values inside `to_signable_string` (or otherwise bind the authenticated headers to the signature check), so the HMAC covers everything the handler subsequently trusts and acts upon, not just the raw body bytes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they fully control) and configures/observes the app's webhook subscription for `orders/create`.
2. Attacker creates an order in their own shop, causing Shopify to POST a webhook to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and a JSON body the attacker fully controls.
3. Attacker captures this request, then resends it to the app's webhook endpoint unchanged except for `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. In `ShopifyAPI::Webhooks::Registry.process`, `Utils::HmacValidator.validate(request)` still succeeds because it only checks `request.to_signable_string` (the untouched body) against the HMAC header — see: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, despite the request never being authenticated as originating from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
