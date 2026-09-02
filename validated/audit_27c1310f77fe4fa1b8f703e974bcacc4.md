## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only, while the `shop-domain` header — the value host applications use to determine *which tenant* the webhook event belongs to — is never included in the signed material. Any actor who can obtain one valid `(body, hmac)` pair signed with the app's shared `api_secret_key` (e.g. a merchant replaying/relaying their own legitimate webhook deliveries) can attach an arbitrary `shop-domain` header to that same signed body and have `ShopifyAPI::Webhooks::Registry.process` accept it as authentic for a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Request#shop` is read straight from the (unauthenticated) header without any binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the body bytes, using the app's `api_secret_key` (same secret for all shops that installed the app): [3](#0-2) 

`Registry.process` then trusts `request.shop` to build the `WebhookMetadata` passed to the handler, after only checking the HMAC (which never touched `shop`): [4](#0-3) 

The identity binding that should hold is: `shop header used to route/attribute the webhook == shop bytes actually signed by the HMAC`. Because `to_signable_string` excludes `shop`, this equality never holds — the gem verifies "bytes were signed with our secret" but not "these bytes were signed *for this shop*".

### Impact Explanation
Because `api_secret_key` is shared across every shop that installs the app, any shop owner (an unprivileged actor with respect to *other* tenants) who can capture one legitimate `(raw_body, hmac)` pair delivered to their own webhook endpoint can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a victim shop's domain. `ShopifyAPI::Webhooks::Registry.process` will accept it, since HMAC validation passes (same body, same secret), and will hand `WebhookMetadata` with the attacker-chosen `shop` to the host application's handler. Any host application logic that trusts `data.shop` to select a session/tenant (a documented, expected usage pattern) can be tricked into acting on/against the wrong tenant's data — a cross-tenant access condition.

### Likelihood Explanation
Exploitability only requires being an installed merchant capable of triggering an ordinary webhook event for their own store (installing the app and performing an action that fires a webhook is normal, unprivileged usage) plus network capture/replay of the HTTP request to the app's own webhook endpoint. No access to `api_secret_key`, no compromised credentials, and no interaction with Shopify's servers beyond normal webhook delivery is required.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`api-version`) header value into the signed material used for HMAC verification, or otherwise cryptographically bind the claimed shop to the signature (e.g., verify the signature per-shop using a shop-specific secret, or include the header as part of `to_signable_string` and require Shopify's signature to cover it). Shopify's webhook HMAC is defined server-side over the body only, so this may require an additional application-level integrity check that ties webhook shop identity to the destination endpoint/registration rather than relying solely on the header.

### Proof of Concept
1. App is installed on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com`, both webhooks signed with the same `Context.api_secret_key`.
2. Attacker triggers a webhook event on their own shop, capturing `raw_body` and `x-shopify-hmac-sha256` for a legitimate delivery to the app's webhook endpoint.
3. Attacker resends the identical `raw_body` and `hmac` header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:13-22` returns `true` because only `raw_body` was signed/verified.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb:189-200` invokes the handler with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from and was authorized for the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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
