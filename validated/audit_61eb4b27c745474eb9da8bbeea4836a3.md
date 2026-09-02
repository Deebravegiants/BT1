### Title
Webhook `shop` (and `topic`/`webhook_id`) identity headers are not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify," but the HMAC signature computed by `ShopifyAPI::Webhooks::Request` only covers the raw JSON body, not the `shop-domain`, `topic`, or `webhook-id` headers that the library passes downstream as the identity of the sending tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are read straight from unauthenticated HTTP headers, independent of the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then forwards `request.shop` (and topic/webhook_id) unchecked into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identity: [3](#0-2) 

The documentation explicitly promises that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request — including the `shop` field surfaced in `WebhookMetadata` — is authenticated. In reality, the HMAC only proves the *body bytes* were signed with the app's `client_secret`; it proves nothing about which shop header accompanied those bytes. This is exactly the "field acted on but not covered by the HMAC" identity-binding break: `shop` (used by the handler to attribute the webhook to a tenant) ≠ `shop` (covered by the signature).

Because a Shopify app's webhook signing secret (`api_secret_key`/`client_secret`) is shared across *all* shops that install the app (it is not shop-specific), any shop that installs the app receives genuine, correctly-signed webhook bodies. The installer of that shop can capture one of these legitimate `(raw_body, hmac)` pairs and replay it to the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` will still pass because it only recomputes the HMAC over `@raw_body`: [4](#0-3) 

The handler then receives `WebhookMetadata` claiming the data came from the victim shop, even though neither the body nor the shop header was ever bound together by the signature.

### Impact Explanation
This breaks the tenant-identity binding the library implicitly promises ("verify the request did indeed come from Shopify" with the `shop` field it hands to handlers). Any app whose webhook handler uses `data.shop` to key persistence, authorization, or cache lookups (a documented and expected usage pattern per `docs/usage/webhooks.md`) can be made to process attacker-controlled body content under a spoofed victim shop identity — a cross-tenant data confusion/injection primitive reachable by any user who can install the app on their own store.

### Likelihood Explanation
Any user can create a free Shopify development store, install a public app, and receive genuinely signed webhooks for topics the app is registered for. Capturing the raw body and the corresponding `x-shopify-hmac-sha256` value requires no special privilege beyond normal app installation, and replaying it with a different `shop-domain` header against the app's public webhook endpoint is trivial.

### Recommendation
Include the identity-carrying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`. At minimum, the `shop` value used downstream should be independently corroborated (e.g., checked against a known/registered shop for this webhook subscription) rather than trusted solely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for `orders/create` webhooks.
2. Shopify delivers a legitimate webhook to the app: body `B`, header `x-shopify-hmac-sha256: H(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends this exact `(B, H)` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only and succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though `B` never originated for `victim-shop`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
