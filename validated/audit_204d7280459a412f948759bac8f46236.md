The OAuth `AuthQuery` HMAC covers `shop` and `host` (both included in `to_signable_string`), so that path is fully bound. The webhook path is the concrete finding.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-attribution forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches to the handler using the `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is never included in the HMAC computation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC (over the body) and then constructs `WebhookMetadata` using `request.shop` verbatim, handing it to the host application's handler as the authenticated tenant identity: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only proves that the *body bytes* were signed with the app's `api_secret_key`; it says nothing about which shop that signature was issued for, because the shop header is outside the signable string: [4](#0-3) 

This breaks the identity binding: `shop header used to route/attribute the event == shop bound by the HMAC`. Since the app's `api_secret_key` is shared across *all* shops that install the app (it is not per-shop), any body+HMAC pair that Shopify legitimately generated for one tenant's webhook remains a **valid signature for that same body under any other shop's domain header**. An attacker who has installed the app on their own store (an unprivileged, non-victim tenant) can capture a legitimate `(body, hmac)` pair Shopify sent them, and replay it to the app's webhook endpoint with the `shop-domain` header changed to a victim's `*.myshopify.com` domain. `Registry.process` will accept it (HMAC over body still checks out) and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability: the shop identity a host application relies on to route webhook data (e.g., to look up the tenant record, apply changes, or trigger side effects keyed by shop) can be forged by any other installer of the same app, without needing that victim's access token or secret. Depending on how the host app's webhook handler uses `data.shop` (e.g., upserting orders/customers, revoking access, redacting data, updating billing state) this enables cross-tenant data pollution or unauthorized actions attributed to a shop the attacker does not control.

### Likelihood Explanation
Exploitation requires only that the attacker (1) install the app themselves (a normal, permission-free step available to any Shopify merchant) so they receive one legitimate webhook with a body+HMAC signed under the app's shared secret, and (2) know or guess a target shop's `*.myshopify.com` domain (publicly discoverable). No access token, `client_secret`, or privileged access is required — this matches an "unprivileged internet user" threat model.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header in the HMAC-signable material, or otherwise cryptographically bind the shop identity to the signature before trusting `request.shop`/`data.shop` in `Registry.process`. At minimum, document that host applications must independently verify the `shop` header against a known-installed shop for that specific token/session before acting on webhook data, since the gem currently provides no such binding.

### Proof of Concept
1. App installs on Attacker's shop `attacker.myshopify.com`. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures this `(B, HMAC)` pair.
3. Attacker POSTs to the app's public webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `OpenSSL.secure_compare(computed_signature, received_signature)` against `to_signable_string` (the raw body), which is unchanged. [5](#0-4) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim.myshopify.com"`, even though `victim.myshopify.com` never sent or authorized this event. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
