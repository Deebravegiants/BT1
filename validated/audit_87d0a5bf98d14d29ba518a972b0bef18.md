### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop once the HMAC check passes, but the HMAC only covers the raw request body — it never binds the `shop`, `topic`, `webhook_id`, or `api_version` values that the gem hands to the developer's handler as trusted metadata.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` computes the received signature from the `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are included in `to_signable_string`: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e. HMAC over the body) and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute `OpenSSL::HMAC.hexdigest(sha256, secret, signable_string)` and compare only that digest — again, `signable_string` for a webhook request is just the raw body: [4](#0-3) 

The documented contract explicitly tells developers that after `process` succeeds, `data.shop` is "The shop domain of the webhook" and can be used to identify which tenant the event belongs to (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) 

The identity binding the gem is supposed to enforce is: `hmac_valid(raw_body) == true` implies `request.shop == "the shop that actually generated raw_body"`. Because `shop` is not part of the signed material, this equality does not hold. Anyone who owns any Shopify store with the app installed (an unprivileged actor with no access to `api_secret_key`) can trigger a legitimate webhook to their own endpoint, capture the genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair Shopify computed with the shared secret, and replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a victim shop they don't control. `HmacValidator.validate` still succeeds (body and HMAC are untouched and mutually consistent), so `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain and the attacker's own webhook body — exactly analogous to the reported bug class where a value acted upon (`unacknowledgeEdge`'s effect) is not covered by the field the signature actually authenticates.

### Impact Explanation
This breaks the shop-identity binding that host applications are documented to rely on for per-tenant webhook processing, enabling cross-tenant data confusion/injection: an attacker can make the app's webhook handler believe attacker-controlled data (order, product, customer events, etc.) originated from a shop they don't own. Depending on how the host app persists/acts on `data.shop` + `data.body` (exactly as the docs recommend), this can lead to writing attacker data into another tenant's records or triggering tenant-scoped side effects — a cross-tenant access issue.

### Likelihood Explanation
The prerequisite is only that the attacker has (or creates) any Shopify development/trial store with the target app installed — no `api_secret_key`, access token, or privileged credential is required, and no host-application misuse beyond following the documented `data.shop` usage is needed. This makes the analog reachable purely through this gem's own `Webhooks::Request`/`Registry.process`/`HmacValidator` code path.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the material that is authenticated, or otherwise cross-check the header-derived shop against an independently trusted value before trusting it in `WebhookMetadata`. Concretely, either:
- Require callers to supply the expected shop for the endpoint/session and assert `request.shop == expected_shop` in `Registry.process` before dispatch, or
- Include the `shop`, `topic`, and `webhook_id` headers as part of the HMAC-signed payload verification (if Shopify's webhook signing scheme allows it), so that tampering with these headers invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no special privilege needed).
2. Attacker triggers a real event (e.g. creates an order) so Shopify sends a genuine webhook to the app's registered endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's real secret).
3. Attacker captures `(B, H)` from their own webhook delivery (e.g. via a proxy they control, or by owning the endpoint if self-hosted for testing).
4. Attacker replays an HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes.
6. `Registry.process` invokes the developer's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and `body == B`, even though `victim-shop` never sent this event.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
