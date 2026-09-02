### Title
Cross-tenant webhook confusion — HMAC covers only the raw body, not the `shop-domain` header trusted for tenant identification - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic solely because `Utils::HmacValidator.validate(request)` returns true, but the HMAC is computed over the raw body only. The `shop` value that the gem hands to the developer's handler (documented as "the shop domain of the webhook") comes from an unauthenticated header and is never bound to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC of the `Request` object and, if it passes, immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body for webhooks) and the shared `Context.api_secret_key`: [4](#0-3) 

The `api_secret_key` (`client_secret`) is a single value shared by the app across **every shop** that installs it — it is not shop-specific. Consequently `hmac(raw_body) == HMAC(raw_body, client_secret)` is a property of the *body content and the app's secret only*; it says nothing about which shop the header claims to be from. An attacker who installs the same app on their own (attacker-controlled) shop will receive genuinely, validly-signed webhook deliveries for their own shop's data (e.g., `orders/create`, `customers/data_request`, `customers/redact`). Because the signature never covers `shop-domain`, the attacker can replay that exact raw body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body and secret are unchanged), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain, per the gem's own documented handler contract: [5](#0-4) 

This breaks the identity binding: `shop asserted by header == shop the app's data-processing logic (following the gem's documented API) will act on`, while the only authenticated quantity is `HMAC-verified bytes == raw_body`, which never includes `shop`.

### Impact Explanation
Apps built per this gem's documented pattern key their persistence/data-processing off `WebhookMetadata.shop` (as shown in the gem's own example: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`). An attacker who has installed the app on any shop (including their own, at zero privilege beyond normal app installation) can forge the tenant binding of webhook deliveries and cause data to be attributed to, or destructive mandatory actions performed against, a different (victim) tenant — e.g. spoofing `customers/redact` or `shop/redact` mandatory GDPR webhooks against an arbitrary victim shop domain. This is a cross-tenant confusion vulnerability arising directly from this gem's `Utils::HmacValidator`/`Webhooks::Request`/`Webhooks::Registry` design, not from the host application deviating from the documented API — the host is doing exactly what the docs instruct.

### Likelihood Explanation
Likelihood is moderate-to-high for any attacker who can install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant/developer) and can also reach the app's public webhook endpoint directly with a forged header set (webhook endpoints are plain HTTP(S) routes, not protected by anything other than this HMAC check).

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signable content that is cryptographically bound to the request, or require the gem's webhook processing to independently corroborate `shop` against an out-of-band authoritative source (e.g., cross-check against the shop that originally registered for `webhook_id`/topic) rather than trusting the raw header value once only the body HMAC has been checked. At minimum, document prominently that `WebhookMetadata.shop` is unauthenticated and must not be used as a sole tenant-scoping key without additional verification.

### Proof of Concept
1. Install the vulnerable app on attacker-owned shop `attacker.myshopify.com`; trigger a real webhook (e.g. `customers/redact`) and capture the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's shared `client_secret`).
2. Replay the exact request to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`, keeping body `B` and `H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, client_secret)` and finds it equals `H` — validation succeeds because `to_signable_string` never included the shop header.
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and invokes the app's handler, which (per the gem's documented pattern) performs the redact/data action scoped to `victim.myshopify.com` even though the payload actually originated from the attacker's own shop.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
